# Video Technique Analysis — Feasibility Experiment Results

**Isolated experiment. Not part of the production FormFit AI application.** No production endpoints, frontend, or coaching agents were modified. No experimental dependency (`opencv-python-headless`) was added to `requirements.txt`.

## 1. Video Inventory (real, measured)

All 11 videos are `.MOV` (QuickTime/H.264, iPhone-recorded), vertical 1080×1920, ~29-30fps.

| File | Size | Resolution | FPS | Duration |
|---|---|---|---|---|
| IMG_2363.MOV | 53.8MB | 1080x1920 | 30.0 | 29.1s |
| IMG_2369.MOV | 81.4MB | 1080x1920 | 30.0 | 44.1s |
| IMG_3018.MOV | 84.2MB | 1080x1920 | 30.0 | 74.9s |
| IMG_3019.MOV | 223.0MB | 1080x1920 | 30.0 | 202.3s |
| IMG_3020.MOV | 258.8MB | 1080x1920 | 30.0 | 230.9s |
| IMG_3022.MOV | 77.7MB | 1080x1920 | 30.0 | 70.2s |
| IMG_3084.MOV | 147.2MB | 1080x1920 | 30.0 | 130.6s |
| IMG_3085.MOV | 13.6MB | 1080x1920 | 28.9 | 12.4s |
| IMG_3087.MOV | 15.1MB | 1080x1920 | 29.0 | 14.1s |
| IMG_E3084.MOV | 126.1MB | 1080x1920 | 29.9 | 113.8s |
| IMG_E3086.MOV | 14.3MB | 1080x1920 | 28.9 | 13.4s |

## 2. Native Video Input Support — Investigated, Not Assumed

Web search of Portkey's documentation found **no mention of a video content type** in its Chat Completions multimodal support — only `image_url` is documented (sources: Portkey OpenAI integration docs, AI Gateway getting-started guide). Combined with the real, observed fact that this project's Portkey route is backed by Azure OpenAI (confirmed by real `azure-openai` error messages in Phase 2 testing), and Azure OpenAI's Chat Completions API likewise only documents image input — **native video input is not supported**. This conclusion is based on actual documentation research, not an assumption that image support implies video support.

**Approach used**: extract representative frames per video and send them as multiple `image_url` blocks in one message — the standard workaround for video-via-vision-LLM, and the only technically available path.

## 3. Proposed and Approved Real API Calls

Exactly 2 real `gpt-6-luna` calls were proposed and approved before being made (see `AI_prompts.md` for the approval record): one per video, each bundling 4 chronologically-ordered frames (10%/40%/60%/90% through the clip) from **two different exercises performed by the same lifter in the same session**: a squat clean (`IMG_E3086.MOV`) and a snatch (`IMG_3085.MOV`), confirmed by direct visual inspection of the frames before and after the calls.

## 4. Results — Call 1: IMG_E3086.MOV (Squat Clean)

**Frame timestamps** (relative to the clip): ~1.3s, ~5.4s, ~8.0s, ~12.1s (10/40/60/90% of 13.4s).

**Model output (verbatim, redacted for no PII — none present):**
> Likely movement: a clean, with a front-squat catch — moderate-to-high confidence... Frame 1: bar on floor, lifter hinged forward... Frame 2: deep squat-like position, bar held high near shoulders/front... near-side plate obscures much of the arm and bar position... Frame 3: more upright, bar still near shoulder level, plate blocks clear view of hands... Frame 4: hinged forward again, reaching toward the bar on the floor. These are neutral position observations, not a judgment of technique. The frames don't show the transitions clearly enough to establish timing or exact bar path.

| Criterion | Assessment |
|---|---|
| **Correct exercise identification** | **Likely correct** (squat clean) — independently cross-checked by direct visual inspection of the actual frames. Model appropriately hedged with "moderate-to-high confidence" rather than certainty. |
| **Observable movement phases** | Correctly described 4 distinct phases matching the 4 frames (floor/hinge → catch/squat → recovery → return to floor) — consistent with what the frames actually show. |
| **Specific technique observations grounded in visible frames** | Minimal and appropriately hedged — the model repeatedly flagged that the weight plate occludes the hands/bar/arms, limiting what it could actually assess. No invented joint angles or fabricated measurements. |
| **Actionable coaching cues** | **None provided.** The system prompt deliberately restricted the model from making technique-fault judgments (per the "never claim... without validation" instruction); the model complied and gave zero coaching cues. This is a direct, expected consequence of the safety-first prompt design, not a model failure — but it means this output alone is **not useful as actual coaching feedback**. |
| **Uncertainty / camera-angle limitations** | Explicitly and repeatedly stated: plate occlusion, inability to infer motion/timing between frames, no claim about what happens between captured frames. |
| **Unsupported/hallucinated claims** | **None detected.** No invented rep count, weight, injury-risk claim, or biomechanical certainty. |
| **Real usage** | `prompt_tokens=9667, completion_tokens=700, cached_tokens=0, reasoning_tokens=468` |
| **Real latency** | `service_ttlt_ms=5059, engine_ttlt_ms=4757, user_visible_ttft_ms=331` |

## 5. Results — Call 2: IMG_3085.MOV (Snatch)

**Frame timestamps**: ~1.2s, ~5.0s, ~7.4s, ~11.2s (10/40/60/90% of 12.4s).

**Model output (verbatim):**
> Frame 1: hinged forward over a loaded barbell... Frames 2-3: standing with the bar high above the head area, arms and bar position partly obscured by the large plate; a fully straight-arm overhead position is not clearly visible. Frame 4: hinged forward again. Likely movement (inference): some kind of barbell lift from the floor to an overhead position — moderate confidence. Whether it is a snatch, a clean and jerk, or another overhead lift is unclear from these views. The plate blocks important details, and these stills don't establish the movement or timing between positions.

| Criterion | Assessment |
|---|---|
| **Correct exercise identification** | **Partially correct, explicitly uncertain.** The model could not distinguish snatch from clean-and-jerk — independently confirmed by visual inspection that this is actually a snatch (direct floor-to-overhead, no visible rack/front-squat catch phase in these frames). The model's refusal to guess rather than confidently naming the wrong lift is a **positive safety behavior**, but it means identification accuracy was genuinely incomplete, not just appropriately hedged. |
| **Observable movement phases** | Only 2 of roughly 3-4 real phases (floor/hinge, overhead) were distinguishable from these 4 frames — the model did not claim to see a turnover/catch transition, which is honest given the frames provided. |
| **Specific technique observations grounded in visible frames** | Very limited — again constrained by plate occlusion blocking the arms/bar. |
| **Actionable coaching cues** | **None** — same safety-prompt constraint as Call 1. |
| **Uncertainty / camera-angle limitations** | Explicitly flagged: occlusion, inability to confirm exact lift type, no claim about inter-frame motion. |
| **Unsupported/hallucinated claims** | **None detected.** |
| **Real usage** | `prompt_tokens=9666, completion_tokens=781, cached_tokens=0, reasoning_tokens=564` |
| **Real latency** | `service_ttlt_ms=6116, engine_ttlt_ms=5859, user_visible_ttft_ms=310` |

## 6. Comparison Against a Simple Manual Observation Checklist

A human coach reviewing the same two clips, even just by eye at normal video speed (not 4 stills), could reasonably assess:

| Checklist item | Human coach (full video) | AI (4 static frames) |
|---|---|---|
| Correct lift identification | Easy — full motion visible | Clean: likely correct; Snatch: explicitly unresolved |
| Bar path (vertical closeness to body) | Observable throughout | **Not assessable** — occlusion + no motion data |
| Catch/turnover speed and depth | Observable | **Not assessable** — static frames carry no tempo/speed information |
| Knee/hip/ankle timing (triple extension) | Observable | **Not assessable** — requires continuous motion |
| Specific, actionable cue (e.g., "catch was slightly forward of midfoot") | A coach could give this immediately | **Not given** — model abstained by design |

**The manual checklist clearly outperforms the 4-frame AI pass on every item that requires motion, timing, or a specific actionable cue** — exactly the limitation the user's instructions anticipated ("four static frames do not constitute full video understanding"). The AI pass's only genuine value in this experiment was a reasonably accurate (for one clip) and appropriately-hedged exercise identification — not uncovering or correcting any real position concern a coach would catch at a glance.

## 7. Conservative Feasibility Assessment

- **Exercise identification from 4 frames**: usable with caveats for a clearly-staged lift (clean), **not reliable** for a lift the model has less visual separation on (snatch vs. clean-and-jerk confusion).
- **Actionable technique feedback**: **not demonstrated** in this experiment — zero coaching cues were produced, by design, because of the safety constraints this exact project's risk assessment requires (see `docs/RISK_REGISTER.md` R1). Removing those constraints to get cues would reintroduce the exact false-precision risk the constraints exist to prevent.
- **Occlusion** (a weight plate blocking the camera's view of the lifter's hands/arms/bar in both clips) was a real, measured limitation independent of the model — a structural problem with single-camera phone footage, not something better prompting fixes.
- **Cost/latency per clip**: ~9,700 prompt tokens and ~5-6 second end-to-end latency per 4-frame analysis — workable for a single on-demand check, not for real-time feedback.
- **No hallucinations or unsupported biomechanical/injury claims occurred** in either real call — the safety-first prompt design worked as intended.

**Overall**: the experiment demonstrates the AI can produce an honest, non-fabricating description with appropriate uncertainty, but **cannot yet produce feedback a CrossFit athlete would find more useful than glancing at their own video** — the core value proposition of "video technique analysis" is not met by this 4-frame approach.
