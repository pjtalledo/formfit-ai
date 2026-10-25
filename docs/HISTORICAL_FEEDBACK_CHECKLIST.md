# FormFit AI — Historical Feedback Checklist

Tracks known grading feedback from prior homeworks in this course so the same deductions are not repeated on the Final Project. Only feedback actually provided by the user is recorded here — nothing is invented for homeworks where no feedback was given.

| Homework | Score (if known) | Known Feedback | FormFit AI Control | Status |
|---|---|---|---|---|
| HW1 | Not provided | Issues noted: exact expected outputs, accounting interpretation, and missing required files | Verify EVALUATION_PLAN.md acceptance criteria specify exact expected outputs per feature (not vague descriptions); verify all mandatory deliverable files (report.html, slides.html, README.md, .env.example) exist before declaring any phase done | **PARTIAL PASS** — README.md and .env.example now exist (Phase 1); report.html/slides.html still missing (scheduled Phase 5). `backend/tests/` enforce exact expected outputs for Pydantic schemas and API status codes, not vague descriptions. |
| HW2 | NOT PROVIDED | NOT PROVIDED | N/A | NOT PROVIDED |
| HW3 | 99/100 | Deduction for missing `.env.example` | `.env.example` is an explicit Phase 5 deliverable in IMPLEMENTATION_ROADMAP.md, with an automated presence check before that phase is marked done (also tracked in RISK_REGISTER.md R13) | **PASS** — `.env.example` created in Phase 1 (contains no real secrets, verified by manual review); confirmed present in the Phase 1 file inventory (AI_prompts.md). |
| HW4 | NOT PROVIDED | NOT PROVIDED | N/A | NOT PROVIDED |
| HW5 | NOT PROVIDED | NOT PROVIDED | N/A | NOT PROVIDED |
| HW6 | 92/100 (initial AI grade) | Deductions for incomplete cache testing and cached tokens appearing in a purported uncached run | EVALUATION_PLAN.md §G requires provider-reported cached-token counts to be logged separately from application-level cache hits, for every run; an "uncached" claim must show zero provider-reported cached tokens in that call's own usage metadata (also tracked in RISK_REGISTER.md R12). Caching experiments must use equivalent workloads across cached/uncached comparisons. | **PARTIAL PASS** — `backend/app/portkey_client.py` and `database.py` log `cached_tokens` separately from prompt/completion tokens (schema field exists and was exercised: the real live run reported `cached_tokens=0`, honestly reflecting a genuinely uncached call, not asserted without evidence). A full cached-vs-uncached comparison experiment has not been run yet — no caching feature has been built. Status remains open until such a comparison exists. |

## Caching Experiment Rule (from HW6)
If FormFit AI implements any caching (prompt caching, application-level response caching, etc.), the comparison between "cached" and "uncached" runs must:
1. Use equivalent workloads (same input, same model, same parameters) for both conditions.
2. Report provider-side cached input tokens (from Portkey/OpenAI usage metadata) separately from any application-level cache-hit flag.
3. Never label a run "uncached" if its own usage metadata reports nonzero provider-side cached tokens.

## Status Legend
- **PENDING** — control is defined in planning docs but has not yet been exercised against real implementation evidence.
- **NOT PROVIDED** — no feedback was given for this homework; nothing is assumed or invented.

This checklist is re-reviewed at the end of every implementation phase alongside TECHNICAL_AUDIT.md and PROFESSOR_GRADING_AUDIT.md.

## Phase 1 Closure Audit Addendum — 2026-10-24
No change to HW1/HW3/HW6 status from this pass (no feature code changed). One cross-cutting hygiene item closed: `.gitignore` now explicitly excludes `.env`, `.venv`, databases, and caches — reinforcing the HW3 `.env.example`/secret-handling control with a corresponding exclude-list, rather than relying on `.env.example` alone.

## Final Consolidated Phase Addendum — 2026-10-25
- **HW1 control** (exact expected outputs, missing required files): reinforced — mobile viewport tests assert exact, specific expected values (body scroll width ≤ viewport width, button height ≥ 44px, exactly 2 file inputs), not vague "looks fine" checks.
- **HW3/HW6 controls**: unchanged, no new evidence this phase (no new API calls, no new caching behavior).
- **New lesson applied**: `.gitignore` was re-audited specifically to exclude raw personal video files (`videos/`, extracted frame images) while preserving the redacted written findings (`experiments/video_feasibility/RESULTS.md`) — a direct application of "exclude secrets/sensitive data, but not required evidence," extended here to personal privacy (identifiable people in video footage) rather than just credentials.

## Final Pre-Submission Audit Addendum — 2026-10-25
- **HW1 control** (exact expected outputs, missing required files): all required files now exist and were verified present in a real, freshly-built clone (`README.md`, `.env.example`, `report.html`, `slides.html`, `.gitignore`) — not just present in the dev working copy.
- **HW3 control** (`.env.example`): re-verified present and secret-free in the actual simulated clone, not assumed from the dev copy.
- **HW6 control** (caching evidence, reproducibility): a **new, real reproducibility defect** was found and fixed this audit — `requirements.txt` pinned `pillow==10.4.0`/`playwright==1.47.0` while the actually-tested versions were `13.0.0`/`1.64.1`. This is the same category of risk as HW6's "invalid uncached baseline" lesson: claiming reproducibility without verifying it against what was actually run. Fixed by re-pinning to the real tested versions and re-verified via a fresh install.

## Phase 3 Addendum — 2026-10-25
- **HW1 control** (exact expected outputs, missing required files): report.html and slides.html now exist, closing the "missing required files" risk that was open through Phase 2. Both were verified against their exact official requirements (10-15 printed pages via real PDF rendering; ≤10 slides via real DOM/Reveal.js check) rather than assumed compliant.
- **HW3 control** (`.env.example`): unchanged, still PASS.
- **HW6 control** (cached vs. uncached tokens): `docs/TOKENOMICS_ANALYSIS.md` explicitly states all real calls this project reported `cached_tokens: 0`, correctly attributed to genuinely uncached first-time calls (no caching feature exists), not asserted blindly.
- **New general lesson applied**: a real defect (KB plural-matching) was found via an actual screenshot during this phase's own evidence-gathering and disclosed, not hidden — directly in the spirit of "never claim a test passed unless it was actually executed" from the project's own validation protocol (AGENTS.md).

## Phase 2 Addendum — 2026-10-25
- **HW1 control** (exact expected outputs, not vague descriptions): strengthened this phase — the 5 real safety/accuracy tests (`docs/TECHNICAL_AUDIT.md` "Phase 2 — WOD Scanner & Robustness") each compare actual model output against a known, specific expected result (exact ground-truth text, exact uncertainty-marker presence, exact absence of invented numbers), not a general "it seemed to work" assessment.
- **HW6 control** (cached vs. uncached token distinction): continues to be exercised honestly — every real call this phase (capability check, 5 safety tests) reported `cached_tokens: 0` from genuine provider usage metadata, consistent with these being first-time, genuinely uncached calls (no caching feature exists yet, so this is expected, not asserted blindly).
- No new HW1/HW3/HW6 gaps identified this phase.
