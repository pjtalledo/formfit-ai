import json

import pytest

from app import agent as agent_module
from app.agent import run_formfit_agent, AgentError
from app.knowledge_base import is_known_exercise
from app.portkey_client import ModelCallError


@pytest.mark.parametrize("name,expected", [
    ("thruster", True), ("Thruster", True), ("THRUSTERS", True),
    ("pull-up", True), ("Pull-ups", True), ("pull-ups", True),
    ("box jumps", True), ("made-up-exercise-xyz", False), ("", False),
])
def test_is_known_exercise_handles_case_and_plurals(name, expected):
    assert is_known_exercise(name) is expected


def _fake_call_model_success(system_prompt, user_prompt, json_mode=True):
    if "WOD parser" in system_prompt:
        # Plural forms ("Thrusters"/"Pull-ups") deliberately match how the
        # real model actually writes exercise names (see a real screenshot
        # that caught KB-matching failing on these exact plurals, fixed in
        # knowledge_base.is_known_exercise — Phase 3, docs/TECHNICAL_AUDIT.md).
        content = json.dumps({
            "format": "For Time",
            "time_cap_minutes": 20,
            "exercises": [
                {"name": "Thrusters", "scheme": "21-15-9", "reps": None, "load_note": None},
                {"name": "Pull-ups", "scheme": "21-15-9", "reps": None, "load_note": None},
            ],
            "notes": None,
        })
    else:
        content = json.dumps({
            "warm_up": ["500m row", "dynamic stretches"],
            "scaling_options": ["reduce load", "banded pull-ups"],
            "main_workout_guidance": "Pace the thrusters, break early.",
            "complementary_exercises": ["dead bug"],
            "safety_notes": ["Stop on sharp pain."],
        })
    return {
        "content": content,
        "prompt_tokens": 120,
        "completion_tokens": 80,
        "cached_tokens": 0,
        "estimated_cost_usd": 0.0,
        "latency_ms": 10,
        "model": "gpt-6-luna",
    }


def test_agent_full_success_path(monkeypatch):
    monkeypatch.setattr(agent_module, "call_model", _fake_call_model_success)
    result = run_formfit_agent("21-15-9 thrusters pull-ups for time", "beginner, goals: x, equipment: none")

    assert result["parsed_wod"].format == "For Time"
    assert len(result["parsed_wod"].exercises) == 2
    assert result["recommendation"].main_workout_guidance
    assert result["usage"]["prompt_tokens"] == 240  # summed across two calls
    assert len(result["trace"]) == 4
    assert all(step["ok"] for step in result["trace"])
    validate_step = result["trace"][1]
    assert "unknown_to_kb" not in validate_step["output_summary"], (
        f"Plural exercise names ('Thrusters'/'Pull-ups') should match the KB's singular "
        f"entries via is_known_exercise(); got: {validate_step['output_summary']}"
    )


def test_agent_flags_unknown_exercise(monkeypatch):
    def fake_call(system_prompt, user_prompt, json_mode=True):
        if "WOD parser" in system_prompt:
            content = json.dumps({
                "format": "For Time",
                "exercises": [{"name": "made-up-exercise-xyz", "scheme": "5 rounds", "reps": None, "load_note": None}],
                "notes": None,
            })
        else:
            content = json.dumps({
                "warm_up": ["jog"], "scaling_options": ["reduce"], "main_workout_guidance": "go",
                "complementary_exercises": [], "safety_notes": [],
            })
        return {"content": content, "prompt_tokens": 10, "completion_tokens": 10, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 1, "model": "gpt-6-luna"}

    monkeypatch.setattr(agent_module, "call_model", fake_call)
    result = run_formfit_agent("some made up workout", "beginner")
    validate_step = result["trace"][1]
    assert "unknown_to_kb" in validate_step["output_summary"]


def test_agent_raises_on_malformed_model_output(monkeypatch):
    def fake_call(system_prompt, user_prompt, json_mode=True):
        return {"content": "not valid json", "prompt_tokens": 1, "completion_tokens": 1, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 1, "model": "gpt-6-luna"}

    monkeypatch.setattr(agent_module, "call_model", fake_call)
    with pytest.raises(AgentError) as exc_info:
        run_formfit_agent("some workout", "beginner")
    assert exc_info.value.trace[-1]["ok"] is False


def test_agent_propagates_model_call_error(monkeypatch):
    def fake_call(system_prompt, user_prompt, json_mode=True):
        raise ModelCallError("simulated API failure")

    monkeypatch.setattr(agent_module, "call_model", fake_call)
    with pytest.raises(AgentError) as exc_info:
        run_formfit_agent("some workout", "beginner")
    assert "simulated API failure" in str(exc_info.value)
    assert exc_info.value.trace[0]["ok"] is False
