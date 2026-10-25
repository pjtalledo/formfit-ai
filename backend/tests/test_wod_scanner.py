"""
Non-live tests for the WOD Scanner: mocked model responses for deterministic
unit coverage (confidence flagging, error propagation), plus API-level
validation tests (content-type, size, empty file, missing credentials).
Real-model safety/accuracy evidence lives in test_live_api.py and
docs/EVALUATION_PLAN.md section H, since genuine prompt-injection resistance
cannot be proven with a mock.
"""
import io

import pytest
from fastapi.testclient import TestClient

from app import agent as agent_module
from app import database as db_module
from app import main as main_module
from app.agent import scan_wod_image_tool, AgentError
from app.main import app
from app.portkey_client import ModelCallError


def _fake_image_call_success(system, user_text, image_base64, mime_type="image/png"):
    return {
        "content": "For Time:\n21-15-9\nThrusters\nPull-ups",
        "prompt_tokens": 200, "completion_tokens": 20, "cached_tokens": 0,
        "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna",
    }


def test_scan_tool_clean_transcription_not_flagged(monkeypatch):
    monkeypatch.setattr(agent_module, "call_model_with_image", _fake_image_call_success)
    result = scan_wod_image_tool("fakebase64", "image/png")
    assert result.low_confidence is False
    assert "Thrusters" in result.extracted_text
    assert result.usage.prompt_tokens == 200


def test_scan_tool_flags_unclear_marker(monkeypatch):
    def fake_call(system, user_text, image_base64, mime_type="image/png"):
        return {
            "content": "For Time:\n21-15-9\n[unclear: possibly Thrusters]\nPull-ups",
            "prompt_tokens": 50, "completion_tokens": 20, "cached_tokens": 0,
            "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna",
        }
    monkeypatch.setattr(agent_module, "call_model_with_image", fake_call)
    result = scan_wod_image_tool("fakebase64", "image/png")
    assert result.low_confidence is True
    assert any("unclear" in n.lower() or "review" in n.lower() for n in result.confidence_notes)


def test_scan_tool_flags_near_empty_output(monkeypatch):
    def fake_call(system, user_text, image_base64, mime_type="image/png"):
        return {"content": "  ", "prompt_tokens": 10, "completion_tokens": 1, "cached_tokens": 0,
                "estimated_cost_usd": 0.0, "latency_ms": 5, "model": "gpt-6-luna"}
    monkeypatch.setattr(agent_module, "call_model_with_image", fake_call)
    result = scan_wod_image_tool("fakebase64", "image/png")
    assert result.low_confidence is True


def test_scan_tool_propagates_model_error(monkeypatch):
    def fake_call(system, user_text, image_base64, mime_type="image/png"):
        raise ModelCallError("simulated vision call failure")
    monkeypatch.setattr(agent_module, "call_model_with_image", fake_call)
    with pytest.raises(AgentError):
        scan_wod_image_tool("fakebase64", "image/png")


# --- API-level validation (no model calls needed) ---

@pytest.fixture()
def client(test_db):
    def _override_get_db():
        yield test_db
    app.dependency_overrides[db_module.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_scan_endpoint_rejects_unsupported_content_type(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert resp.status_code == 415


def test_scan_endpoint_rejects_empty_file(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert resp.status_code == 422


def test_scan_endpoint_rejects_heic_with_actionable_message(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("photo.heic", io.BytesIO(b"fake-heic-bytes"), "image/heic")},
    )
    assert resp.status_code == 415
    assert "Most Compatible" in resp.json()["detail"]


def test_scan_endpoint_rejects_oversized_file(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    monkeypatch.setattr(main_module, "MAX_IMAGE_BYTES", 10)  # force a tiny limit for the test
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("big.png", io.BytesIO(b"x" * 1000), "image/png")},
    )
    assert resp.status_code == 413


def test_scan_endpoint_blocked_without_credentials(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: False)
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("test.png", io.BytesIO(b"fake-png-bytes"), "image/png")},
    )
    assert resp.status_code == 503
    assert "BLOCKED" in resp.json()["detail"]


def test_scan_endpoint_success_mocked(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    monkeypatch.setattr(agent_module, "call_model_with_image", _fake_image_call_success)
    resp = client.post(
        "/api/wod/scan",
        files={"image": ("test.png", io.BytesIO(b"fake-png-bytes"), "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Thrusters" in body["extracted_text"]
    assert body["low_confidence"] is False
