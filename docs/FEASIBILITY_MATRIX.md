# FormFit AI — Feasibility Matrix (Revised — official rubric + deadline known)

Legend: **GO** = reliably implementable before the 2026-10-26 6:00 PM deadline with acceptable accuracy/safety. **CONDITIONAL GO** = feasible but requires scope limits, human-in-the-loop, or disclaimers to be reliable; status gated on a POC. **NO-GO** = not reliably achievable in the remaining time; must not be promised in the final report.

**Model correction**: all entries below use the course-approved **`gpt-6-luna`** via Portkey (previously misstated as `gpt-5.6-luna`). `gpt-6-luna`'s multimodal/image-input capability is **unverified** — this is now the single biggest feasibility swing factor for Features 2 and 7 and must be checked in Phase 1 before any vision-dependent feature is built (see ARCHITECTURE.md §0).

| # | Feature | Verdict | Key Models/Libraries | Effort | Reliability Notes |
|---|---------|---------|----------------------|--------|--------------------|
| 1 | Athlete Profile & Onboarding | **GO** | FastAPI + Pydantic + DB | Low | Standard CRUD form; no AI risk. Required for the vertical slice. |
| 2 | AI WOD Scanner (whiteboard photo → text) | **CONDITIONAL GO** | `gpt-6-luna` via Portkey **if it supports image input** (unverified); else `OPENAI_API_KEY` fallback at personal expense, requires approval | Medium | Now a **priority MVP feature** per reprioritization. OCR-style extraction of handwriting is error-prone; must show extracted text to user for confirmation/edit before use. Gated on Phase 1 multimodal capability check. |
| 3 | AI WOD Generator | **GO** | `gpt-6-luna` text + structured output (Pydantic schema) + exercise knowledge base | Medium | Reliable if constrained to a curated exercise library and validated against equipment/experience constraints. Core of the vertical slice. |
| 4 | Movement Scaling & Technique Guidance | **GO** | Static/curated knowledge base referenced by the generator/agent, optionally RAG-assisted | Low-Medium | Reprioritized as MVP (replaces broad "Technique Library" framing); content curated, not freely generated. |
| 5 | Video Technique Analysis | **NO-GO for this deadline** | Frame extraction + multimodal LLM; optional pose estimation | High | Explicitly reclassified as **conditional stretch only** per reprioritization — given the Oct 26 deadline, there is not enough time to run the POC (needs a video dataset that does not yet exist), build, and safety-test this feature. Must NOT be promised in the final report unless actually implemented and tested before the deadline, which is considered unlikely. |
| 6 | Corrective & Complementary Exercises | **CONDITIONAL GO** | Text LLM grounded in curated corrective-exercise knowledge base, triggered by technique-guidance (Feature 4) and/or user-reported limitations — decoupled from Feature 5 to stay in scope | Medium | Reprioritized as MVP, but redesigned to depend on Feature 4 (curated guidance) and profile data rather than Feature 5 (video analysis), since Feature 5 is NO-GO for this deadline. |
| 7 | AI Barbell & Weight Scanner | **CONDITIONAL GO (stretch)** | `gpt-6-luna` vision (unverified) or fallback model | Medium-High | Explicitly reclassified as **conditional stretch only** per reprioritization — same occlusion/ambiguity risks as before, plus the added `gpt-6-luna` capability uncertainty. Do not promise in the final report unless implemented and tested. |
| 8 | Nutrition & Recovery Coach | **CONDITIONAL GO (stretch)** | Text LLM with general evidence-based guidelines + safety disclaimers | Low-Medium | Reclassified as "advanced nutrition" stretch per reprioritization; basic version is cheap but not required for the vertical slice. |
| 9 | Training History Persistence / Dashboard | **GO** | DB + simple charts (React) | Low-Medium | Reprioritized as MVP ("Training history persistence"); standard storage/visualization, no AI reliability risk. |
| 10 | Agent/Tool Orchestration | **GO (now a graded requirement, not optional)** | Single orchestrating agent with explicit tool calls (WOD generation, knowledge-base lookup, persistence) and captured execution traces | Medium | Directly graded under "Agent design" (10 pts). Must produce real, inspectable agent traces — not a simulated or hard-coded flow. |
| 11 | Tokenomics (usage/cost logging) | **GO (now a graded requirement)** | Portkey/API usage metadata capture + documented pricing table | Low-Medium | Directly graded (8 pts). Must log actual token counts and compute real costs from documented pricing — no invented numbers. Must distinguish provider-side cached tokens from application-level cache hits (HW6 lesson, see RUBRIC_COMPLIANCE.md). |
| 12 | Safety defenses (tested) | **GO (now a graded requirement)** | Input validation, curated-knowledge-base constraints, prompt-injection test suite | Medium | Directly graded (8 pts). "Tested" means reproducible prompt-injection test cases with recorded pass/fail results, not a design description. |

## Overall Technical Feasibility Verdict
**GO for a graded, demonstrable MVP by the Oct 26 deadline**, built around Features 1, 3, 4, 9, 10, 11, 12, with Feature 2 (WOD Scanner) included as a priority MVP feature gated on a same-day `gpt-6-luna` multimodal capability check, and Feature 6 (Corrective/Complementary) included as MVP but decoupled from video analysis. Features 5 (Video Technique Analysis), 7 (Barbell Scanner), and 8 (advanced Nutrition) are reclassified as **conditional stretch only** and must not appear in the final report as delivered capabilities unless actually built and tested before the deadline — treat that as unlikely given the timeline.

## Revised MVP Recommendation (deadline-driven)
**MVP (must-have for the vertical slice and grading):**
1. Athlete Profile & Onboarding
3. AI WOD Generator (agent-orchestrated, structured output)
4. Movement Scaling & Technique Guidance (curated)
6. Corrective & Complementary Exercises (curated, decoupled from video)
9. Training History Persistence / Dashboard
10. Agent/Tool Orchestration with captured traces
11. Tokenomics (real token/cost logging)
12. Tested safety defenses (prompt-injection suite)

**Priority MVP, capability-gated:**
2. AI WOD Scanner with mandatory user confirmation — proceed only after Phase 1 confirms `gpt-6-luna` supports image input (or an approved fallback model is authorized).

**Conditional stretch only (do not promise in final report unless implemented and tested):**
5. Video Technique Analysis
7. AI Barbell & Weight Scanner
8. Advanced Nutrition & Recovery Coach
