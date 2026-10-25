# FormFit AI — Architecture (Phase 0, Corrected)

No code is implemented in this phase. This describes the simplest reliable architecture evaluated for later phases.

## 0. Model Correction (supersedes earlier Phase 0 draft)
The course-provided `PORTKEY_API_KEY` permits **`gpt-6-luna` only** — earlier references to `gpt-5.6-luna` in this doc set were incorrect and are corrected throughout. `gpt-5.6-luna` must not be used with the course key.
- `gpt-6-luna`'s actual image-input/multimodal capability has **not yet been verified**. Features 2 (WOD Scanner) and, if pursued, 7 (Barbell Scanner) depend entirely on multimodal input support. This must be verified with a minimal, approved test call (capability check only, not a feature call) before any vision-dependent feature is built — see IMPLEMENTATION_ROADMAP.md Phase 1.
- Fallback: if `gpt-6-luna` does not support image input, `OPENAI_API_KEY` with a compatible multimodal model may be used **at personal expense**, requiring explicit approval before any paid call.
- No API calls of any kind have been made yet in this project; nothing about `gpt-6-luna`'s capabilities should be assumed until verified.

## 1. High-Level Components
- **Frontend**: React (SPA). Simple, component-driven; no SSR complexity needed for an academic project.
- **Backend**: Python/FastAPI. Chosen over Flask/Django for native async support, automatic OpenAPI docs, and first-class Pydantic integration.
- **AI Layer**: LLM calls routed through **Portkey** to **`gpt-6-luna`** (course-approved model), with `OPENAI_API_KEY` + a compatible model as an approved-only, personal-expense fallback if `gpt-6-luna` lacks required multimodal support. Config must search for `.env` first in the repository root, then in its parent directory (per official deliverable requirements). API key never hard-coded or logged.
- **Structured Output Validation**: Pydantic models define strict schemas for every LLM response consumed by the app (WOD structure, scan extraction, technique observations, weight estimates) — rejects/retries malformed output rather than trusting free text.
- **Database**: A single persistent relational store (e.g., SQLite for development/demo simplicity, with a clear upgrade path to Postgres) holding athlete profiles, workouts, sets/reps/weights, PRs, and technique-observation logs.
- **Exercise Knowledge Base**: A curated, versioned dataset (JSON/DB table) of exercises, scaling options, and corrective drills. Used to constrain LLM generation (Features 3, 4, 6) rather than relying on free generation — this is the primary safety/accuracy control.
- **Optional RAG**: Only if the curated knowledge base grows large enough that prompt-stuffing becomes unreliable; not required for MVP scale.
- **Agents/Tool Calling**: A single orchestrating agent is sufficient for MVP (profile + WOD generation + dashboard). Multi-agent decomposition (e.g., separate "scanner agent", "technique agent") should only be introduced if/when Features 5–7 are built, since each has a genuinely distinct input modality and failure mode. Avoid multi-agent architecture purely for demonstration value — it must earn its complexity.
- **Testing/Evaluation Harness**: Automated unit tests for backend logic + a small labeled evaluation set (see EVALUATION_PLAN.md) for each AI-dependent feature, run before any feature is marked complete.

## 2. Data Flow (MVP)
1. User completes onboarding → stored via FastAPI → DB.
2. User requests WOD → backend assembles context (profile, history, equipment) → calls LLM via Portkey → validates against Pydantic schema → constrains exercises to knowledge base → returns structured WOD to frontend.
3. User logs results (sets/reps/weights, optionally via WOD Scanner for whiteboard input) → stored in DB → surfaced on Dashboard.

## 3. Why This Is the Simplest Reliable Option
- Avoids premature multi-agent orchestration (added complexity with no demonstrated MVP benefit).
- Pydantic structured validation is the main defense against LLM hallucination/unsafe output — simpler and more auditable than complex guardrail chains.
- A single relational DB is sufficient for a single-user/demo-scale academic project; no need for distributed storage.

## 4. Course-Concept Alignment
This architecture touches: prompt design and structured output validation, multimodal input handling, human-in-the-loop correction for AI uncertainty, agent/tool orchestration, token/cost accounting, and evaluation of AI reliability — which map directly to the official rubric's Agent design, Tokenomics, Safety, and Application-works categories (see RUBRIC_COMPLIANCE.md). No row of the rubric may be marked PASS until implemented and evidenced; this section only states intended alignment, not achieved compliance.

## 5. Explicitly Deferred Architectural Decisions
- Choice of pose-estimation library for Video Technique Analysis (if pursued) — deferred to Phase 1 POC.
- Hosting/deployment target — not needed until a deployable milestone is approved.
