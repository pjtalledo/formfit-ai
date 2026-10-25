# FormFit AI — Evaluation Plan (Revised — official rubric + deadline known)

No experiments have been run yet. This defines proof-of-concept experiments and acceptance criteria to validate before full implementation of each feature. **No test results are reported here** — none have been executed. Required inputs (sample images/videos, API access) are called out explicitly as MISSING where applicable. All model references use the corrected, course-approved **`gpt-6-luna`**.

## 0. Model Capability Check — EXECUTED 2026-10-25, RESULT: PASS

**This is the single, approved capability test; no additional paid capability-test calls have been or will be made without further approval, per instruction.**

- **Test image**: a synthetic CrossFit whiteboard image (`backend/tests/fixtures/sample_whiteboard.png`), generated locally with PIL, containing the clearly readable text:
  ```
  WOD OF THE DAY
  For Time:
  21-15-9
  Thrusters (95/65 lb)
  Pull-ups
  ```
- **Call**: one real request to `gpt-6-luna` via Portkey (`client.chat.completions.create`) with a `user` message containing both a text prompt and an `image_url` content block (base64-encoded PNG, `data:image/png;base64,...`).
- **1. Does the API accept image input?** **YES.** The call succeeded (HTTP-level success via the OpenAI SDK, no `ModelCallError`) — Portkey/`gpt-6-luna` accepted the `image_url` content block without rejection.
- **2. Does the model actually interpret the image correctly (not just accept it)?** **YES — verified by comparing output to the known ground truth, not assumed from mere API acceptance.** The model's response was:
  ```
  WOD OF THE DAY

  For Time:
  21-15-9
  Thrusters (95/65 lb)
  Pull-ups
  ```
  This is an exact match to the text actually drawn into the test image — a genuine visual-understanding result, not a guess.
- **3. Extracted movements, repetitions, weights, format**: format = "For Time"; rep scheme = "21-15-9"; movements = "Thrusters" (weight: 95/65 lb) and "Pull-ups" — all correctly extracted.
- **4. Token usage (from real provider usage metadata, not estimated)**: `prompt_tokens=258`, `completion_tokens=81`, `total_tokens=339`, `cached_tokens=0` (from `prompt_tokens_details.cached_tokens`), `reasoning_tokens=45` (from `completion_tokens_details`).
- **5. Latency**: `user_visible_ttft_ms=385`, `engine_ttlt_ms=670`, `service_ttlt_ms=895` (from Portkey's `latency_checkpoint` usage field).
- **6. Errors**: none. Call completed successfully on the first attempt.

**Conclusion**: `gpt-6-luna` via Portkey genuinely supports image input for WOD-whiteboard-style transcription, confirmed by matching output against a known ground truth, not merely by the API call succeeding. **Proceeding with full WOD Scanner implementation** (Priority 1 of Phase 2), per the "if supported" branch. The `OPENAI_API_KEY` fallback is not needed.

**Caveat**: this test used one clean, synthetic, clearly-legible image. It does not by itself establish accuracy on messy real handwriting, poor lighting, or heavily occluded whiteboards — those remain open questions for the broader WOD Scanner evaluation in section A below, which still requires a mandatory user-confirmation step regardless of this capability check's success.

## A. AI WOD Scanner (whiteboard photo → structured WOD) — priority MVP
- **POC**: Feed 10-15 sample whiteboard photos (varied handwriting, lighting, formats: AMRAP/EMOM/For Time) to the multimodal LLM; compare extracted text/structure to a manually transcribed ground truth.
- **Acceptance criteria**: ≥80% of workouts correctly extracted (exercise names + rep/round scheme) without user correction; 100% of extraction results are shown to the user for confirmation before being saved (non-negotiable, regardless of accuracy).
- **Missing**: No sample whiteboard photo dataset currently exists in the project directory. **MISSING — needs to be collected/sourced before POC can run.** Also blocked on §0 (model capability check).

## B. AI WOD Generator
- **POC**: Generate 10 WODs across varied profiles (beginner/intermediate/advanced, different equipment sets) and manually review for: exercise safety/appropriateness, equipment compliance, and format correctness.
- **Acceptance criteria**: 100% of generated exercises exist in the curated knowledge base (zero hallucinated movements); 100% equipment-compliant; structured output validates against Pydantic schema with zero schema failures across the 10 runs.
- **Missing**: Curated exercise knowledge base does not yet exist. **MISSING — must be authored before this POC.**

## C. Video Technique Analysis (conditional stretch only — not in MVP)
- **POC**: Extract frames from 5-10 sample technique videos (known movements, ideally with at least one known technical flaw each) and have the multimodal LLM describe observable technique; compare against a human-coach assessment of the same videos.
- **Acceptance criteria**: LLM output must (1) only describe what is visually observable, (2) express calibrated uncertainty language rather than false precision, (3) agree with human-coach flagged issues in ≥60% of cases flagged by the coach as a POC bar (not a production bar), (4) never fabricate a quantitative angle/measurement it cannot support.
- **Missing**: No sample technique video dataset exists in the project directory. **MISSING — needs representative videos (ideally with known ground-truth flaws) before POC can run.** Given the Oct 26 deadline, this POC is unlikely to be run; the final report must not claim this feature unless it actually is.

## D. AI Barbell & Weight Scanner (conditional stretch only — not in MVP)
- **POC**: Photograph/collect 10-15 barbell images with known actual loaded weight (varied plate colors, partial occlusion, asymmetric loading, kg and lb plates) and compare model output to ground truth.
- **Acceptance criteria**: Model must either (a) correctly identify the weight within the plates visibly readable, or (b) explicitly flag uncertainty/request confirmation rather than guess — zero silent fabrication of unseen plate values; ≥70% correct identification on clearly visible, unoccluded setups as a POC bar.
- **Missing**: No sample barbell/plate image dataset exists. **MISSING — needs to be collected before POC can run.** Same deadline caveat as Feature C.

## F. Agent/Tool Orchestration (new — graded requirement)
- **POC**: Run the end-to-end flow (profile → WOD generation → persistence) and capture the actual agent execution trace (tool calls made, order, inputs/outputs).
- **Acceptance criteria**: Trace shows genuine tool invocation (not a hard-coded sequence disguised as agentic); trace is reproducible across repeated runs with the same input; trace is saved as evidence for the report's Agents section.
- **Missing**: No orchestration code exists yet — to be built in Phase 1.

## G. Tokenomics — usage and cost logging (new — graded requirement)
- **POC**: Make one real, approved API call through Portkey to `gpt-6-luna` and capture the usage metadata (prompt tokens, completion tokens, cached tokens if reported) returned by the provider.
- **Acceptance criteria**: Every logged call records actual token counts from provider usage metadata (never estimated/invented) and a cost computed from a documented, cited pricing source. If caching is implemented, provider-reported cached-token counts must be logged and displayed **separately** from any application-level cache-hit flag; a run claimed "uncached" must show zero provider-reported cached tokens in its own usage metadata for that call (direct fix for the HW6 deduction).
- **Missing**: Documented `gpt-6-luna` pricing not yet collected. **MISSING — must be sourced/confirmed before cost calculations can be considered real rather than placeholder.**

## H. Safety — prompt-injection defenses (new — graded requirement)
- **POC**: Construct a small reproducible set of prompt-injection test cases (e.g., attempts to override system instructions, extract the API key, or force unsafe exercise/load recommendations) and run them against the deployed agent.
- **Acceptance criteria**: 100% of test cases are blocked or safely deflected; results are logged with pass/fail per case; the test suite itself is checked into the repo so teaching staff can re-run it.
- **Missing**: Test case set does not yet exist — to be authored in Phase 1/2.

## I. Impact / comparison metric (new — graded requirement)
- **POC**: Define one measurable before/after or comparison metric (e.g., time to produce a personalized WOD manually vs. via FormFit AI, or a side-by-side comparison against an existing CrossFit app/template).
- **Acceptance criteria**: Metric is measured with real timing/comparison data, not estimated; recorded with method described so teaching staff can verify.
- **Missing**: Comparison baseline (existing product or manual process) not yet selected. **MISSING — must be chosen before this can be measured.**

## J. General Evidence Rules
- **No fabrication**: measurements, screenshots, user feedback, and API results must never be invented. If a metric cannot be measured, it is reported as not measured — not estimated and presented as real.
- **Screenshots**: both successful and failed runs must be captured as evidence for the report, not only the best-case outcome.
- **User trial**: if a real user trial is available before the deadline, record it; if not, explicitly state "no user trial conducted" rather than simulating one.
- **API access check**: `PORTKEY_API_KEY` presence in root `.env` should be verified (without printing its value) before any POC requiring live API calls. **Not yet verified — no API calls have been made in this project.**
- **Regression baseline**: Once MVP features are built, re-run all POC evaluation sets after any change to prompts, schemas, or the knowledge base, and report PASS/FAIL per acceptance criterion (per AGENTS.md validation protocol).
