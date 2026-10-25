# FormFit AI — Implementation Roadmap (Revised: Vertical-Slice Strategy)

Deadline: **Monday, October 26, 2026, 6:00 PM**. No phase beyond Phase 0 is authorized yet — each phase requires explicit sign-off before starting, per the course's validation protocol. This roadmap replaces the earlier skeleton-only Phase 1 with an executable, end-to-end-first strategy, since "Application works" (15 pts) and "Teaching staff can run it" (5 pts) require a real running flow, not isolated components.

## Phase 0 — Project Setup & Feasibility Audit (complete, this correction pass)
- Verified directory, corrected model name (`gpt-6-luna`, not `gpt-5.6-luna`), incorporated the official 100-point rubric and deadline, reprioritized MVP, rewrote this roadmap.
- No code, no Git init, no dependency installs, no API calls.

## Phase 1 (proposed) — Minimal End-to-End Vertical Slice
**Goal**: one complete, working path from input to saved, displayed, evidenced output — not a UI skeleton or isolated backend stub.

Steps:
1. Accept athlete information (minimal profile form/endpoint: goals, experience, equipment).
2. Process one sample WOD (hand-typed text input — scanner image path deferred to Phase 2) through `gpt-6-luna` via Portkey.
3. Validate the model's response against a Pydantic schema (reject/retry on malformed output).
4. Generate one personalized recommendation (scaled WOD) from the validated result.
5. Display it in a minimal React interface.
6. Save the result to the DB (SQLite).
7. Capture the agent's execution trace and the call's real token/cost usage metadata.

**Acceptance criteria**:
- A single manual run completes steps 1-7 without a crash, using one real (approved) API call.
- The saved DB record and the captured trace/usage log are inspectable afterward.
- `.env` is read from the repo root first, then parent directory, per the operational requirement.

**Verification commands** (to be defined precisely once the stack exists; placeholders now):
- `pytest` (or equivalent) exit code 0 for backend unit tests covering the Pydantic schema validation.
- Manual run log showing steps 1-7 completed, with the saved DB row and trace/usage JSON attached as evidence.

**Gate**: this slice must demonstrably work end-to-end, with evidence captured, before Phase 2 starts. "Working" is not assumed — it is demonstrated via the verification commands above.

## Phase 2 (proposed) — WOD Scanner + Robustness
- Phase 0 model-capability check (EVALUATION_PLAN.md §0): confirm whether `gpt-6-luna` supports image input.
  - If yes: implement WOD photo extraction with mandatory user-confirmation step before any scanned WOD is saved.
  - If no: escalate for approval of the `OPENAI_API_KEY` fallback before proceeding with this feature.
- Expand profile intake, movement scaling, and technique guidance using the curated knowledge base.
- Add corrective/complementary exercise recommendations (decoupled from video analysis, per FEASIBILITY_MATRIX.md).
- **Acceptance criteria**: WOD Scanner extraction never auto-saves without user confirmation; scaling/technique/corrective recommendations only draw from the curated knowledge base (zero hallucinated exercises in a 10-run manual check).
- **Gate**: PASS/FAIL reported against EVALUATION_PLAN.md sections A, B before Phase 3.

## Phase 3 (proposed) — Genuine Agent Orchestration + Tokenomics
- Replace any hard-coded call sequence with real tool-calling/agent orchestration (per EVALUATION_PLAN.md §F).
- Implement token/cost logging from provider usage metadata with documented pricing (per EVALUATION_PLAN.md §G), explicitly separating provider-side cached tokens from application-level cache hits.
- **Acceptance criteria**: agent trace is reproducible and inspectable; every logged call shows real token counts and a cost computed from cited pricing; no "zero cached tokens" claim without usage-metadata evidence for that call.
- **Gate**: PASS/FAIL reported against EVALUATION_PLAN.md sections F, G before Phase 4.

## Phase 4 (proposed) — Safety Testing + Impact Metric
- Build and run the reproducible prompt-injection test suite (EVALUATION_PLAN.md §H).
- Define and measure the impact/comparison metric (EVALUATION_PLAN.md §I).
- Collect real screenshots of both successful and failed runs.
- **Acceptance criteria**: 100% of safety test cases logged with pass/fail; impact metric measured with real data, not estimated.
- **Gate**: PASS/FAIL reported against EVALUATION_PLAN.md sections H, I before Phase 5.

## Phase 5 (proposed) — Deliverables: Repo, Report, Slides
- Initialize Git repository (only once explicitly authorized), add `README.md` and `.env.example` (never real secrets) — explicit automated check for `.env.example` presence before this phase is marked done (HW3 lesson).
- Verify clean-clone-to-running in under 10 minutes, on a separate test clone.
- Write `report.html` (10-15 printed pages, 8 sections in order: Title+links, Motivation, What is new, Agents, Tokenomics, Safety, Impact, Limits+next steps), with embedded real screenshots.
- Build `slides.html` (max 10 slides, reveal.js, embedded screenshots/diagrams).
- Optional 2-3 minute demo video.
- **Acceptance criteria**: fresh-clone test passes within 10 minutes; report and slides contain only features actually implemented and tested — no promised-but-unbuilt stretch features (video analysis, barbell scanner, advanced nutrition) unless genuinely delivered.

## Phase 6 (proposed) — Independent Audit
- Grader-style audit from a clean copy of the final deliverable, re-running all verification commands and the fresh-clone test.
- Final regression pass across all EVALUATION_PLAN.md sections; update RUBRIC_COMPLIANCE.md rows from PENDING to PASS/FAIL with evidence links, or leave PENDING if genuinely unverified.

## Explicit Non-Assumptions
- The application is not considered "working" until Phase 1's end-to-end slice is actually run and evidenced — this roadmap does not assume success at any gate.
- Stretch features (video analysis, barbell scanning, advanced nutrition) remain conditional; they only enter the roadmap if an earlier phase finishes with time to spare before Oct 26, 6:00 PM, and even then are gated on their own POC evidence (EVALUATION_PLAN.md §C/D).
