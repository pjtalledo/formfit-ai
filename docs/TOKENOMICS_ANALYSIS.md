# FormFit AI — Tokenomics Analysis

All token counts and latencies below are **real, measured values** from actual `gpt-6-luna`/Portkey API responses made during Phases 1–2 of this project (see `AI_prompts.md` for the full call log). **No authoritative published price exists for `gpt-6-luna`** — it is a course-specific model alias routed through Portkey to an Azure OpenAI backend (confirmed by real error messages: `"azure-openai error: ..."`), and no pricing field is returned anywhere in the API response or headers (verified by inspecting a full raw response, including `usage`, `routing`, and `content_filter_results` — no cost field exists). **Every dollar figure below is an explicitly labeled hypothetical assumption, never a verified price.**

## 1. Real Measured Token Usage (actual API responses)

| Operation | Prompt tokens | Completion tokens | Cached tokens | Notes |
|---|---|---|---|---|
| WOD Scan (image, clean) | 258–429 | 76–81 | 0 | Varies with image size/text density |
| WOD Scan (image, ambiguous/blurry) | 310 | 206 | 0 | More completion tokens spent explaining uncertainty |
| WOD Scan (image, injection attempt) | 491 | 102 | 0 | Larger image + longer system prompt |
| Text WOD parse only | 191 | 107 | 0 | Short, vague input |
| Full agent run (parse + recommendation combined) | 393–395 | 982–1,019 | 0 | Two LLM calls summed |
| Trivial text call ("say hi in 3 words") | 13 | 32 | 0 | Baseline floor |

**Cached tokens were 0 in every real call made** — consistent with genuine first-time (uncached) requests, not asserted blindly (see `docs/HISTORICAL_FEEDBACK_CHECKLIST.md` HW6 control). No caching feature is implemented in this project, so 0 is the expected and correctly-reported value, not evidence either way about caching behavior under load.

## 2. Real Measured Latency

| Metric | Observed range | Source |
|---|---|---|
| `user_visible_ttft_ms` (time to first token, user-perceived) | 156–385 ms | Real `latency_checkpoint` fields from Portkey responses |
| `service_ttlt_ms` (total service time to last token) | 397–895 ms | Same |
| End-to-end full agent run (2 sequential LLM calls) | ~2,100–2,300 ms | Sum of two real runs' step durations in `backend/app/agent.py` traces (1218+1062ms and similar) |

## 3. Real Measured Optimization Insight (not hypothetical)

Comparing the real data above: **image-based WOD Scan calls use roughly 1.5–2.5x more prompt tokens than a text-only parse call of similar complexity** (258–491 vs. 191 tokens), and the scan's own system prompt is proportionally larger relative to payload. This is a genuine, measured finding from this project's own API calls, not a hypothesis: **downscaling/compressing whiteboard photos before upload (e.g., to ~1024px max dimension) is a concrete, testable optimization candidate** for reducing per-scan token cost, since image token cost in vision models is typically a function of image resolution. This specific experiment (compress vs. uncompressed image, compare prompt_tokens) has **not yet been run** — it is identified as a next-step experiment, not claimed as already measured.

## 4. Cost Modeling — EXPLICITLY HYPOTHETICAL, NOT A VERIFIED PRICE

Because no real `gpt-6-luna` price exists, the figures below use a **labeled placeholder rate** (`$X.XX` per million input tokens, `$Y.YY` per million output tokens — left as variables, not asserted as real numbers) purely to illustrate the *shape* of a cost model a real price could be substituted into. **Do not read any dollar amount in this section as a real cost** — none is claimed.

### Cost per operation (formula, not a number)
```
cost_per_scan        = (scan_prompt_tokens / 1e6 * input_rate) + (scan_completion_tokens / 1e6 * output_rate)
                      ≈ (370 / 1e6 * input_rate) + (120 / 1e6 * output_rate)   [using real average measured tokens]

cost_per_coaching_plan = (parse_prompt + rec_prompt) / 1e6 * input_rate + (parse_completion + rec_completion) / 1e6 * output_rate
                        ≈ (394 / 1e6 * input_rate) + (1000 / 1e6 * output_rate)   [using real average measured tokens]

cost_per_complete_workflow = cost_per_scan + cost_per_coaching_plan   (if the user scans a whiteboard, worst case)
                            ≈ (764 / 1e6 * input_rate) + (1120 / 1e6 * output_rate)
```

### Monthly cost per user — explicit usage assumption
**Assumption (not measured, stated explicitly)**: an active CrossFit athlete logs one WOD per day, roughly 50% via scan and 50% typed, for 22 training days/month.
```
monthly_calls_per_user ≈ 22 workouts × 1 coaching-plan call + 11 scan calls
monthly_cost_per_user  = 22 × cost_per_coaching_plan + 11 × cost_per_scan   [still a function of unknown input_rate/output_rate]
```
No dollar figure is computed here, since `input_rate`/`output_rate` are unknown. Once real pricing is sourced, this formula can be evaluated directly.

### Scaling estimates — 100 and 10,000 users
```
total_monthly_cost(N users) = N × monthly_cost_per_user
```
At 100 users: `100 × monthly_cost_per_user`. At 10,000 users: `10,000 × monthly_cost_per_user`. Both remain symbolic pending real pricing — presenting a specific dollar figure here would violate the explicit instruction never to invent a verified price.

## 5. Required Follow-Up (before any dollar figure can be claimed in the final report)
1. Ask the course instructor or Portkey dashboard administrator for the actual contracted rate for `gpt-6-luna` under this course's Portkey workspace (the model is not a standard published-price product, so no public price page exists to cite).
2. If a real rate is obtained, substitute it into the formulas in section 4 to produce real, citable dollar figures.
3. Run the image-compression optimization experiment described in section 3 and report its real measured token delta.

## Status
**Tokenomics evidence: real measured tokens/latency — PASS. Real dollar-cost figures: PENDING (blocked on sourcing an authoritative price), explicitly not fabricated.**
