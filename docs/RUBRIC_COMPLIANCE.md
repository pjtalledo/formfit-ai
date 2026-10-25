# FormFit AI — Rubric Compliance

## Status: PENDING (rubric now known; implementation evidence not yet produced)

The local placeholder file [`Final Project/project_requirements.html`](../project_requirements.html) ("TBD... Details coming soon") is **outdated**. The project owner has since received the actual official Final Project requirements directly, which supersede the placeholder page. This document now tracks against those official requirements.

## Official Deadline
**Monday, October 26, 2026, 6:00 PM.**

## Official Grading Breakdown (100 points)

| Category | Points | Evidence Status |
|---|---|---|
| Novelty + real-world value | 21 | PENDING |
| Application works | 15 | PENDING |
| Teaching staff can run it | 5 | PENDING |
| Look + feel | 10 | PENDING |
| Motivation + differentiation | 8 | PENDING |
| Agent design | 10 | PENDING |
| Tokenomics | 8 | PENDING |
| Safety | 8 | PENDING |
| Impact | 5 | PENDING |
| Report design | 2 | PENDING |
| Slide content | 6 | PENDING |
| Slide design | 2 | PENDING |
| **Total** | **100** | — |

No row may be marked PASS until the corresponding feature is implemented, tested, and has supporting evidence (traces, logs, screenshots, measurements) per [EVALUATION_PLAN.md](EVALUATION_PLAN.md). Nothing has been implemented as of this update — all rows are PENDING.

## Mandatory Deliverables (tracked, all PENDING)
1. GitHub repository URL. — **PENDING** (no Git repo initialized yet; explicitly not authorized until Phase 1 approval).
2. `report.html` — 10-15 printed pages, embedded screenshots, eight sections in order: Title+links, Motivation, What is new, Agents, Tokenomics, Safety, Impact, Limits+next steps. — **PENDING**
3. `slides.html` — max 10 slides, reveal.js, embedded screenshots/diagrams. — **PENDING**
4. Optional 2-3 minute demo video. — **PENDING / OPTIONAL**

## Operational Requirements (tracked, all PENDING)
- App must run online or from a fresh clone within 10 minutes. — **PENDING**
- Local setup must search for `.env` first in the repo root, then in its parent directory. — **PENDING** (must be implemented in app startup/config loading logic in Phase 1).
- Repo must contain `README.md` and `.env.example`, and must never contain real secrets. — **PENDING**. Explicit lesson applied from HW3 (99/100, deduction for missing `.env.example`): `.env.example` creation and a pre-commit/CI-style check for its presence will be built in from Phase 1, not added late.
- Teaching staff will test the app directly — reliability and clean-clone setup are graded, not assumed.

## Consequence for Prior Phase 0 Claims
The Phase 0 feasibility and architecture docs were written before the official rubric was known and assumed general best practices rather than these specific weights. [FEASIBILITY_MATRIX.md](FEASIBILITY_MATRIX.md) and [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) have been revised accordingly (see "Revised GO/CONDITIONAL GO/NO-GO" and the vertical-slice roadmap). Nothing in this document or elsewhere in `docs/` should be read as implying any feature is built or tested — that status is PENDING until Phase 1+ produces actual evidence.

## Lessons From Prior Homework Grading (to avoid repeat deductions)
- **HW3 (99/100)**: deducted for missing `.env.example`. → `.env.example` is a Phase 1 deliverable, checked explicitly before any "done" claim.
- **HW6 (92/100 initial AI grade)**: deducted for incomplete cache testing and cached tokens appearing in a purported "uncached" run. → Any caching implementation must explicitly distinguish provider-side cached tokens (reported by the API's usage metadata) from application-level cache hits, and an "uncached run" claim must be backed by usage metadata showing zero cached tokens for that call, not asserted without evidence (see [EVALUATION_PLAN.md](EVALUATION_PLAN.md)).
