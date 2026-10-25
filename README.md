# FormFit AI

Adaptive AI CrossFit coaching platform — Yale SOM MGT 409 Final Project.

**Status: Phase 1 (end-to-end vertical slice).** Video Technique Analysis, automatic
Barbell/Weight Scanning, and advanced Nutrition coaching are **not implemented** in
this phase — see [docs/FEASIBILITY_MATRIX.md](docs/FEASIBILITY_MATRIX.md).

## What this does

1. Create an athlete profile (experience, goals, equipment, limitations, weight unit).
2. Type a WOD, **or scan a whiteboard photo** — `gpt-6-luna` via Portkey supports image
   input (verified with a real capability check, see `docs/EVALUATION_PLAN.md` §0) and
   transcribes it to plain text. The scanned text always appears in the same editable
   box as typed input and is never submitted automatically — you review/correct it
   before generating a plan. If part of the image is unclear, the scanner says so
   explicitly (`[unclear: ...]`) rather than guessing.
3. The FormFit AI agent (`backend/app/agent.py`) parses the WOD, validates it against
   a curated exercise knowledge base, and generates a personalized warm-up, scaling
   options, main-workout guidance, and complementary exercises — using the
   course-approved `gpt-6-luna` model via Portkey.
4. The result, plus real token usage/cost and the full agent execution trace, is
   displayed in the browser and saved to a local SQLite database.

## Requirements

- Python 3.10+
- A `PORTKEY_API_KEY` with access to `gpt-6-luna`

## Setup (should take well under 10 minutes)

**Important: every command below must be run with `Final Project/` as your
current directory — not `MGT 409 AI/` (its parent) and not any subfolder.**
Running from the wrong directory, or with the wrong Python interpreter (not
this project's own `.venv`), is the most common startup failure (e.g.
`No module named uvicorn` means you are not using this project's `.venv`).

1. `cd` into this folder (`Final Project/`).
2. Copy `.env.example` to `.env` **in this folder, or in its parent folder** — the
   app checks this folder first, then the parent, for `.env`.
3. Create the virtual environment and install dependencies **using this
   project's own `.venv`** (do not reuse a `.venv` from a different folder):

```bash
python -m venv .venv
pip install -r requirements.txt
```

   - Windows: use `.venv\Scripts\python.exe` to run the install (as shown
     below) instead of activating, to avoid ambiguity about which `python`
     is on your PATH:
     ```bash
     .venv\Scripts\python.exe -m pip install -r requirements.txt
     ```
   - macOS/Linux: `source .venv/bin/activate && pip install -r requirements.txt`

4. Run the server **from this folder** with `--app-dir backend` (this exact
   flag is required — `app/main.py` uses absolute imports like `from app.config
   import ...`, which only resolve correctly when `backend/` is the import
   root):

```bash
# Windows
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload

# macOS/Linux
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload
```

5. Open **http://localhost:8000** in a browser. The React frontend (`frontend/index.html`)
   is served directly by the backend. React, ReactDOM, and Babel are **vendored locally**
   under `frontend/vendor/` (downloaded once, committed to the repo) — the page does not
   depend on any CDN at runtime, so it works even with no internet access after cloning,
   and is immune to corporate/campus firewalls blocking a CDN.

**Verify it worked** (optional, no browser needed):
```bash
curl http://localhost:8000/api/health
# expect: {"status":"ok","model_configured":true,"approved_model":"gpt-6-luna"}
```

## Running tests

Run from this folder (`Final Project/`):

```bash
.venv\Scripts\python.exe -m pytest backend/tests -v
```

Tests that require a live API call are marked and will report **SKIPPED** (not
PASSED) if `PORTKEY_API_KEY` is not configured — see
`backend/tests/test_live_api.py`.

**Frontend smoke tests** (`backend/tests/test_frontend_smoke.py`) render the real
page in headless Chromium via Playwright and check the actual DOM, not just the
HTTP status code — this is what caught the blank-page bug (see Known Limitations
below, and `docs/TECHNICAL_AUDIT.md` "Frontend Blank Page Fix"). One-time setup:

```bash
.venv\Scripts\python.exe -m playwright install chromium
```

This downloads a Chromium build (can take a few extra minutes depending on
connection) and is only needed to run the frontend smoke tests — not to run the
app itself. If Playwright or its browser isn't installed, these tests are
**SKIPPED** (not passed), same policy as the live API tests.

## Project layout

```
Final Project/
  backend/app/         FastAPI backend, agent orchestration, DB models
  backend/tests/        Automated tests (incl. real-browser frontend smoke tests)
  frontend/index.html   React UI (vendored React/Babel, no build step, no CDN)
  frontend/vendor/       Locally vendored React, ReactDOM, Babel standalone
  docs/                 Product, feasibility, architecture, risk, evaluation, audit docs
  .env.example          Template for required credentials (no real secrets)
```

## Mobile-First

FormFit AI is designed for the typical real-world use case: an athlete at the gym,
on their phone, photographing a whiteboard WOD. Verified (via real browser-engine
testing, Chromium + WebKit/Safari, at 375x812, 390x844, 393x852, and 412x915) to
render with no horizontal overflow, touch-friendly 44px+ controls, and a readable
layout at all four viewports, plus desktop. The WOD-scan input offers both **Take
Photo** (opens the phone camera) and **Choose from Gallery**. **This is browser-engine
emulation, not testing on a physical iPhone or Android device** — no physical-device
compatibility claim is made. See `docs/TECHNICAL_AUDIT.md` "Mobile-First Verification"
for full detail, including two real cross-browser bugs found and fixed during testing.

**Supported image formats**: JPEG, PNG, WebP. **HEIC/HEIF (default iPhone format) is
not supported** — no conversion is performed; uploading a HEIC photo returns a clear
message asking the user to switch their iPhone's camera format to "Most Compatible"
or pick a JPEG/PNG photo instead. This is a deliberate choice to never silently accept
an unverified format.

## Known Limitations (Phase 2)

- **Frontend bug fixed 2026-10-25 (see `docs/TECHNICAL_AUDIT.md` "Frontend Blank
  Page Fix" / "Edge Caching Discrepancy").** The page previously rendered the
  black-and-pink header but nothing else, because Babel standalone's default JSX
  runtime emitted an ES module `import` statement into a non-module script. Fixed
  by compiling the app source manually with the classic JSX runtime, vendoring
  React/ReactDOM/Babel locally, and adding an explicit `Cache-Control` header so
  browsers always revalidate instead of serving a stale cached page. **User-confirmed
  working in Microsoft Edge.**
- **WOD photo scanning is implemented and verified working** (`POST /api/wod/scan`),
  confirmed via a real capability check (`docs/EVALUATION_PLAN.md` §0) and 5 further
  real-API safety/accuracy tests (`docs/TECHNICAL_AUDIT.md` Phase 2 entry) covering
  prompt injection (text and image), ambiguous/illegible images, and missing
  information — all with zero fabricated content.
- **Pricing is a documented placeholder.** `gpt-6-luna` pricing has not been
  published/confirmed anywhere in this project; `backend/app/portkey_client.py`
  marks its cost constant as `UNVERIFIED` and real token counts are always logged
  even though the dollar cost is not yet trustworthy.
- Video Technique Analysis, Barbell/Weight Scanner, and advanced Nutrition Coach
  are conditional stretch features, not implemented here.
- The 5 Phase 2 safety tests were genuine but ad-hoc manual API calls, not yet
  packaged into a repeatable automated test suite (a real gap, not hidden).

See `docs/TECHNICAL_AUDIT.md` and `docs/PROFESSOR_GRADING_AUDIT.md` for the full
evidence-based assessment of what is and is not working.

## Final Project Deliverables

- **`report.html`** — the required 8-section report (Title+links, Motivation, What is
  new, Agents, Tokenomics, Safety, Impact, Limits+next steps), with real embedded
  screenshots and agent-trace evidence. Verified to render as **12 printed Letter-size
  pages** via real headless-Chromium PDF rendering (not HTML length) — within the
  required 10-15 page range.
- **`slides.html`** — a 9-slide reveal.js deck (≤10 required), verified to actually
  render via a real headless-browser check (not just the presence of the script tag).
- **`docs/TOKENOMICS_ANALYSIS.md`** — real measured token/latency data; no fabricated
  dollar costs, since no authoritative `gpt-6-luna` price exists.
- **`docs/SAFETY_EVIDENCE.md`** — 5 real adversarial/accuracy tests with redacted real
  traces, explicitly distinguishing provider-level from application-level defenses.
- **`docs/IMPACT_EVALUATION.md`** — a ready-to-run real-user evaluation protocol and
  feedback form; explicitly labeled PENDING since no real users have been evaluated yet.
- **`docs/COMPETITIVE_ANALYSIS.md`** — based on an actual web search, with cited sources
  and explicit non-claims where the research could not confirm competitor features.
