import pytest
from fastapi.testclient import TestClient

from app import database as db_module
from app.main import app
from app import main as main_module
from app.agent import AgentError


@pytest.fixture()
def client(test_db):
    # Route FastAPI's get_db dependency to the isolated test session.
    def _override_get_db():
        yield test_db

    app.dependency_overrides[db_module.get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_endpoint_no_secrets_exposed(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "approved_model" in body
    assert body["approved_model"] == "gpt-6-luna"
    assert "api_key" not in str(body).lower().replace("api key", "")
    assert "PORTKEY_API_KEY" not in str(body)


def test_create_and_fetch_profile(client):
    resp = client.post("/api/profiles", json={
        "name": "Taylor", "experience_level": "beginner", "goals": "build strength",
        "equipment": ["dumbbells"], "limitations": "", "weight_unit": "lb",
    })
    assert resp.status_code == 200
    profile_id = resp.json()["id"]

    fetched = client.get(f"/api/profiles/{profile_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Taylor"


def test_create_profile_invalid_experience_level_rejected(client):
    resp = client.post("/api/profiles", json={
        "name": "Bad", "experience_level": "superhuman", "goals": "x", "equipment": [],
    })
    assert resp.status_code == 422


def test_get_nonexistent_profile_returns_404(client):
    resp = client.get("/api/profiles/999999")
    assert resp.status_code == 404


def test_wod_endpoint_blocked_without_credentials(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: False)
    profile_resp = client.post("/api/profiles", json={
        "name": "NoKey", "experience_level": "beginner", "goals": "x", "equipment": [],
    })
    profile_id = profile_resp.json()["id"]

    resp = client.post("/api/wod", json={"athlete_id": profile_id, "raw_text": "21-15-9 thrusters", "source": "typed"})
    assert resp.status_code == 503
    assert "BLOCKED" in resp.json()["detail"]


def test_wod_endpoint_404_for_unknown_athlete(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    resp = client.post("/api/wod", json={"athlete_id": 999999, "raw_text": "21-15-9 thrusters", "source": "typed"})
    assert resp.status_code == 404


def test_wod_endpoint_rejects_too_short_input(client):
    profile_resp = client.post("/api/profiles", json={
        "name": "Short", "experience_level": "beginner", "goals": "x", "equipment": [],
    })
    profile_id = profile_resp.json()["id"]
    resp = client.post("/api/wod", json={"athlete_id": profile_id, "raw_text": "hi", "source": "typed"})
    assert resp.status_code == 422


def test_wod_endpoint_surfaces_agent_failure_as_502(client, monkeypatch):
    monkeypatch.setattr(main_module, "credentials_configured", lambda: True)
    profile_resp = client.post("/api/profiles", json={
        "name": "Fail", "experience_level": "beginner", "goals": "x", "equipment": [],
    })
    profile_id = profile_resp.json()["id"]

    def fake_agent(raw_text, profile_summary):
        raise AgentError("simulated failure", [{"tool": "parse_wod_tool", "ok": False}])

    monkeypatch.setattr(main_module, "run_formfit_agent", fake_agent)
    resp = client.post("/api/wod", json={"athlete_id": profile_id, "raw_text": "21-15-9 thrusters pull-ups", "source": "typed"})
    assert resp.status_code == 502
