import base64
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import credentials_configured, APPROVED_MODEL
from app.database import init_db, get_db, AthleteProfile, WorkoutResult
from app.schemas import ProfileCreate, ProfileOut, WodRequest, WodResponse, WodScanResult
from app.agent import run_formfit_agent, scan_wod_image_tool, AgentError

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB — enough for a phone photo, caps abuse/cost

# HEIC/HEIF (the default photo format on iPhones) is NOT supported by the
# approved model's image_url input and no server-side conversion dependency
# has been added for this deadline (lowest-risk choice: a clear rejection
# message beats silently accepting a format we haven't tested end-to-end —
# see docs/TECHNICAL_AUDIT.md "Mobile-First Verification"). Some mobile
# browsers (notably iOS Safari) already auto-convert HEIC to JPEG during the
# file-picker upload, but this has not been verified on a physical device,
# so a raw HEIC/HEIF upload must be rejected with actionable guidance, not
# a generic error.
HEIC_TYPES = {"image/heic", "image/heif"}

app = FastAPI(title="FormFit AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache_for_dev(request, call_next):
    """
    FastAPI's StaticFiles sends only Last-Modified/ETag, no Cache-Control.
    Without an explicit directive, browsers apply heuristic caching and can
    silently serve a stale, previously-broken copy of frontend/index.html
    from disk cache without even checking the network — this is exactly what
    happened when a real Edge session kept showing a fixed bug after reload
    (see docs/TECHNICAL_AUDIT.md "Edge Caching Discrepancy"). Forcing
    no-cache (revalidate-on-every-request, not no-store) still allows cheap
    304 responses via the existing ETag, so this doesn't disable caching
    entirely or weaken anything security-relevant — it only guarantees the
    browser always re-checks freshness instead of trusting a guess.
    """
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "model_configured": credentials_configured(), "approved_model": APPROVED_MODEL}


@app.post("/api/profiles", response_model=ProfileOut)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    record = AthleteProfile(
        name=profile.name,
        experience_level=profile.experience_level,
        goals=profile.goals,
        equipment=profile.equipment,
        limitations=profile.limitations,
        weight_unit=profile.weight_unit,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ProfileOut(id=record.id, **profile.model_dump())


@app.get("/api/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    record = db.get(AthleteProfile, profile_id)
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut(
        id=record.id,
        name=record.name,
        experience_level=record.experience_level,
        goals=record.goals,
        equipment=record.equipment,
        limitations=record.limitations or "",
        weight_unit=record.weight_unit,
    )


@app.post("/api/wod/scan", response_model=WodScanResult)
async def scan_wod(image: UploadFile = File(...)):
    if not credentials_configured():
        raise HTTPException(status_code=503, detail="BLOCKED: PORTKEY_API_KEY is not configured")

    if image.content_type in HEIC_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                "HEIC/HEIF photos aren't supported yet. On iPhone, go to "
                "Settings > Camera > Formats and switch to 'Most Compatible', "
                "or choose a JPEG/PNG photo instead."
            ),
        )
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{image.content_type}'. Allowed: {sorted(ALLOWED_IMAGE_TYPES)}",
        )

    data = await image.read()
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail=f"Image exceeds the {MAX_IMAGE_BYTES // (1024 * 1024)}MB limit")

    try:
        result = scan_wod_image_tool(base64.b64encode(data).decode(), image.content_type)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=f"WOD image scan failed: {exc}") from exc

    return result


@app.post("/api/wod", response_model=WodResponse)
def process_wod(req: WodRequest, db: Session = Depends(get_db)):
    if not credentials_configured():
        raise HTTPException(status_code=503, detail="BLOCKED: PORTKEY_API_KEY is not configured")

    profile = db.get(AthleteProfile, req.athlete_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Athlete profile not found")

    profile_summary = (
        f"{profile.experience_level} athlete, goals: {profile.goals}, "
        f"equipment: {', '.join(profile.equipment) or 'none'}, "
        f"limitations: {profile.limitations or 'none'}, units: {profile.weight_unit}"
    )

    try:
        result = run_formfit_agent(req.raw_text, profile_summary)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=f"Agent workflow failed: {exc}") from exc

    record = WorkoutResult(
        athlete_id=req.athlete_id,
        source=req.source,
        raw_input=req.raw_text,
        parsed_wod=result["parsed_wod"].model_dump(),
        recommendation=result["recommendation"].model_dump(),
        model_used=result["usage"]["model"],
        prompt_tokens=result["usage"]["prompt_tokens"],
        completion_tokens=result["usage"]["completion_tokens"],
        cached_tokens=result["usage"]["cached_tokens"],
        estimated_cost_usd=result["usage"]["estimated_cost_usd"],
        agent_trace=result["trace"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return WodResponse(
        id=record.id,
        parsed_wod=result["parsed_wod"],
        recommendation=result["recommendation"],
        usage={**result["usage"]},
        agent_trace=result["trace"],
    )


@app.get("/api/athletes/{athlete_id}/history")
def get_history(athlete_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(WorkoutResult)
        .filter(WorkoutResult.athlete_id == athlete_id)
        .order_by(WorkoutResult.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "parsed_wod": r.parsed_wod,
            "recommendation": r.recommendation,
            "prompt_tokens": r.prompt_tokens,
            "completion_tokens": r.completion_tokens,
            "cached_tokens": r.cached_tokens,
            "estimated_cost_usd": r.estimated_cost_usd,
        }
        for r in records
    ]


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
