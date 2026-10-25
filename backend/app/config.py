"""
Loads .env per the official deliverable requirement: search the repo root
(Final Project/) first, then its parent directory (MGT 409 AI/).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
PARENT_DIR = REPO_ROOT.parent

ENV_SOURCE = None
root_env = REPO_ROOT / ".env"
parent_env = PARENT_DIR / ".env"

if root_env.exists():
    load_dotenv(root_env)
    ENV_SOURCE = str(root_env)
elif parent_env.exists():
    load_dotenv(parent_env)
    ENV_SOURCE = str(parent_env)

PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
APPROVED_MODEL = "gpt-6-luna"
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")

DB_PATH = REPO_ROOT / "backend" / "formfit.db"


def credentials_configured() -> bool:
    return bool(PORTKEY_API_KEY)
