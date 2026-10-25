# FormFit AI — Product Requirements (Phase 0)

## 1. Overview
FormFit AI is an adaptive AI CrossFit coaching platform built for the Final Project of Yale SOM's AI Foundations for Managers course. It targets beginner, intermediate, and advanced CrossFit athletes and covers Olympic Weightlifting, Gymnastics, Strength, Conditioning, Mobility, and Recovery.

Priority: a reliable, functional, demonstrable application — not a polished-looking prototype with unproven capabilities.

## 2. Users & Personas
- **Beginner**: needs scaling, technique education, conservative load guidance.
- **Intermediate**: needs programming variety, progress tracking, moderate technique feedback.
- **Advanced**: needs precise load tracking, PR history, nuanced technique cues.

## 3. Core Workflow
Profile → Daily WOD → Personalized Warm-up & Scaling → Training → Technique Analysis & Weight Logging → Corrective Work → Recovery → Progress Tracking → Next Workout Adaptation.

## 4. Proposed Capabilities (as requested; feasibility assessed separately in FEASIBILITY_MATRIX.md)
1. Athlete Profile & Onboarding — goals, experience, training frequency, equipment, kg/lb preference, limitations.
2. AI WOD Scanner — extract workouts from whiteboard photos.
3. AI WOD Generator — personalized daily/complementary workouts based on goals, equipment, history, readiness.
4. Exercise Technique Library — execution, mistakes, scaling, progressions.
5. Video Technique Analysis — analyze observable technique in uploaded exercise videos.
6. Corrective Exercise Engine — drills/accessory/mobility recommendations from technical observations.
7. AI Barbell & Weight Scanner — recognize plates/markings, compute load where evidence supports it, quick logging.
8. Nutrition & Recovery Coach — general evidence-based guidance (not medical/clinical advice).
9. Athlete Dashboard — workouts, sets, reps, weights, PRs, progress history.
10. Adaptive Coaching — uses history + technical observations to refine future recommendations.

## 5. Non-Functional Requirements
- **Reliability**: features must work on representative real inputs, not just happy-path demos.
- **Safety**: no fabricated weights, no unsafe corrective/medical claims; clear disclaimers on nutrition/recovery and injury-adjacent content; tested (not just designed) prompt-injection defenses, per the official rubric's Safety category.
- **Privacy**: user images/videos and health-adjacent data handled minimally; no secrets committed; `.env` never exposed; repo must never contain real secrets (`.env.example` only).
- **Cost control / tokenomics**: no paid API calls without explicit approval; Portkey + **`gpt-6-luna`** (course-approved model — corrected from an earlier draft's `gpt-5.6-luna`, which the course key does not permit) per project rules; actual token usage and cost must be logged with documented pricing, not estimated.
- **Deadline**: official Final Project deadline is **Monday, October 26, 2026, 6:00 PM**. Scope must be achievable in the remaining time, not a full semester.
- **Reproducibility**: the app must run online or from a fresh clone within 10 minutes; config must search for `.env` first in the repo root, then in its parent directory; repo must include `README.md` and `.env.example`.

## 6. Out of Scope (Phase 0)
No frontend, backend, database, or application code is implemented in this phase. Implementation begins only after explicit Phase 1 approval.

## 7. Reprioritized MVP (per official rubric + deadline)
Priority order for implementation: (1) Athlete onboarding/profile, (2) WOD photo extraction + user confirmation, (3) Personalized WOD generation, (4) Movement scaling & technique guidance, (5) Corrective & complementary exercises, (6) Training history persistence, (7) Genuine agent/tool orchestration, (8) Actual token usage & cost logging, (9) Tested safety defenses. Video analysis, automatic barbell plate recognition, and advanced nutrition are **conditional stretch features only** — not to be promised in the final report unless actually implemented and tested. See FEASIBILITY_MATRIX.md for full rationale.

## 8. Open Items
- Official Final Project rubric and deadline are now known (see RUBRIC_COMPLIANCE.md) — the local `project_requirements.html` placeholder is outdated and superseded.
- `gpt-6-luna`'s multimodal/image-input capability is unverified and must be checked in Phase 1 before building the WOD Scanner.
