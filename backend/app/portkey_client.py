"""
Thin wrapper around the OpenAI SDK pointed at the Portkey gateway.
Only the course-approved APPROVED_MODEL is ever used. No silent model
substitution — if the key is missing, callers must treat this as BLOCKED,
never fall back to a different model without explicit approval.
"""
import json
import time

from openai import OpenAI

from app.config import PORTKEY_API_KEY, PORTKEY_BASE_URL, APPROVED_MODEL

# Documented placeholder pricing (USD per 1M tokens) — gpt-6-luna pricing has
# not been published/confirmed anywhere in this project yet. This value MUST
# be replaced with a cited, documented source before any real cost claim is
# made in the final report (see docs/EVALUATION_PLAN.md section G).
PRICING_PER_MILLION_TOKENS_UNVERIFIED = {"input": 0.0, "output": 0.0}
PRICING_SOURCE = "UNVERIFIED — placeholder, not a real pricing citation"


class ModelCallError(Exception):
    pass


def _client() -> OpenAI:
    if not PORTKEY_API_KEY:
        raise ModelCallError("PORTKEY_API_KEY is not configured")
    return OpenAI(api_key=PORTKEY_API_KEY, base_url=PORTKEY_BASE_URL, timeout=30.0)


def _parse_response(response, start: float) -> dict:
    latency_ms = int((time.monotonic() - start) * 1000)
    usage = response.usage
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0

    # Provider-side cached tokens, if reported, live under prompt_tokens_details.
    cached_tokens = 0
    details = getattr(usage, "prompt_tokens_details", None)
    if details is not None:
        cached_tokens = getattr(details, "cached_tokens", 0) or 0

    cost = (
        prompt_tokens / 1_000_000 * PRICING_PER_MILLION_TOKENS_UNVERIFIED["input"]
        + completion_tokens / 1_000_000 * PRICING_PER_MILLION_TOKENS_UNVERIFIED["output"]
    )

    return {
        "content": response.choices[0].message.content,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cached_tokens": cached_tokens,
        "estimated_cost_usd": cost,
        "latency_ms": latency_ms,
        "model": APPROVED_MODEL,
    }


def call_model(system_prompt: str, user_prompt: str, json_mode: bool = True) -> dict:
    """
    Makes one real call to the course-approved model. Returns a dict with
    keys: content (str), prompt_tokens, completion_tokens, cached_tokens,
    estimated_cost_usd, latency_ms, model. Raises ModelCallError on failure —
    never fabricates a response.
    """
    client = _client()
    start = time.monotonic()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        response = client.chat.completions.create(
            model=APPROVED_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            timeout=30.0,
            **kwargs,
        )
    except Exception as exc:  # network/auth/model errors — surfaced, not swallowed
        raise ModelCallError(f"{APPROVED_MODEL} call failed: {exc}") from exc

    return _parse_response(response, start)


def call_model_with_image(system_prompt: str, user_text: str, image_base64: str, mime_type: str = "image/png") -> dict:
    """
    Same contract as call_model, but attaches an image to the user message.
    Confirmed working against the course-approved model via a real capability
    check (see docs/EVALUATION_PLAN.md §0 and docs/TECHNICAL_AUDIT.md "WOD
    Scanner Capability Check") — gpt-6-luna via Portkey does accept image
    input. No json_mode here: vision prompts ask for plain transcribed text,
    not structured JSON, to avoid the model guessing structure for illegible
    content.
    """
    client = _client()
    start = time.monotonic()
    try:
        response = client.chat.completions.create(
            model=APPROVED_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
                    ],
                },
            ],
            timeout=30.0,
        )
    except Exception as exc:
        raise ModelCallError(f"{APPROVED_MODEL} image call failed: {exc}") from exc

    return _parse_response(response, start)
