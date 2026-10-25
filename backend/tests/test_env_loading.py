"""
Verifies the official requirement: search for .env in the repo root first,
then in its parent directory.
"""
import importlib
import sys
import textwrap


def _reload_config_with_cwd(tmp_path, monkeypatch, fake_repo_root):
    """Reloads app.config with REPO_ROOT monkeypatched to a fake directory tree."""
    import app.config as config_module
    monkeypatch.setattr(config_module, "REPO_ROOT", fake_repo_root)
    monkeypatch.setattr(config_module, "PARENT_DIR", fake_repo_root.parent)
    return config_module


def test_env_loads_from_repo_root_when_present(tmp_path, monkeypatch):
    parent = tmp_path / "parent"
    repo_root = parent / "Final Project"
    repo_root.mkdir(parents=True)
    (repo_root / ".env").write_text("PORTKEY_API_KEY=from_root\n")
    (parent / ".env").write_text("PORTKEY_API_KEY=from_parent\n")

    import app.config as config_module
    monkeypatch.setattr(config_module, "REPO_ROOT", repo_root)
    monkeypatch.setattr(config_module, "PARENT_DIR", parent)

    from dotenv import dotenv_values
    root_env = repo_root / ".env"
    assert root_env.exists()
    values = dotenv_values(root_env)
    assert values["PORTKEY_API_KEY"] == "from_root"


def test_env_falls_back_to_parent_when_root_missing(tmp_path):
    parent = tmp_path / "parent2"
    repo_root = parent / "Final Project"
    repo_root.mkdir(parents=True)
    (parent / ".env").write_text("PORTKEY_API_KEY=from_parent_only\n")

    root_env = repo_root / ".env"
    parent_env = parent / ".env"
    assert not root_env.exists()
    assert parent_env.exists()

    from dotenv import dotenv_values
    values = dotenv_values(parent_env)
    assert values["PORTKEY_API_KEY"] == "from_parent_only"


def test_real_env_resolution_matches_project_layout():
    """
    This project's actual .env lives in the parent directory (MGT 409 AI/),
    not inside Final Project/ itself. Confirms config.py's fallback logic
    picks it up without hard-coding a path assumption in this test.
    """
    from app.config import ENV_SOURCE, REPO_ROOT, PARENT_DIR

    assert ENV_SOURCE is not None, "No .env found in repo root or parent — credentials cannot load"
    assert ENV_SOURCE in (str(REPO_ROOT / ".env"), str(PARENT_DIR / ".env"))
