"""
Real, end-to-end calls to gpt-6-luna via Portkey. These are SKIPPED (not
PASSED) when PORTKEY_API_KEY is not configured, and genuinely call the API
otherwise — results are never fabricated. Run deliberately, not on every
save, since each run makes a real (billable, if the course key is metered)
API call.
"""
import pytest

from app.config import credentials_configured
from app.portkey_client import call_model, ModelCallError
from app.agent import run_formfit_agent, AgentError

requires_credentials = pytest.mark.skipif(
    not credentials_configured(), reason="PORTKEY_API_KEY not configured — skipping live API test"
)


@requires_credentials
def test_live_model_capability_check():
    """Minimal probe: confirms gpt-6-luna responds at all via Portkey."""
    try:
        result = call_model(
            "Respond with strict JSON only.",
            'Return exactly: {"ok": true}',
            json_mode=True,
        )
    except ModelCallError as exc:
        pytest.fail(f"Live capability check failed — model/credential issue: {exc}")

    assert result["model"] == "gpt-6-luna"
    assert result["prompt_tokens"] > 0
    assert result["completion_tokens"] > 0


@requires_credentials
def test_live_end_to_end_agent_run():
    """Real end-to-end run through the full agent pipeline."""
    try:
        result = run_formfit_agent(
            "For Time: 21-15-9 Thrusters, Pull-ups",
            "beginner athlete, goals: general fitness, equipment: barbell, pull-up bar, limitations: none, units: lb",
        )
    except AgentError as exc:
        pytest.fail(f"Live end-to-end agent run failed: {exc}")

    assert result["parsed_wod"].exercises
    assert result["recommendation"].main_workout_guidance
    assert result["usage"]["prompt_tokens"] > 0
    assert len(result["trace"]) == 4
