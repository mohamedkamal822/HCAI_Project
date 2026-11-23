import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(PROJECT_DIR / ".env")

SIGNS_PATH = BACKEND_DIR / "signs.json"
ALIASES_PATH = BACKEND_DIR / "aliases.json"
VIDEOS_DIR = PROJECT_DIR / "dataset"
FRONTEND_DIR = PROJECT_DIR / "frontend"
# Audit logs are runtime data. Keep them outside the source tree so static
# development servers (for example VS Code Live Server) do not reload the UI
# after every chat request. Set ISHARA_DATA_DIR to choose a persistent location.
DATA_DIR = Path(os.getenv("ISHARA_DATA_DIR", Path(tempfile.gettempdir()) / "ishara"))
LOGS_DIR = DATA_DIR / "logs"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_TRACES = 200
MAX_INPUT_CHARACTERS = 300
RELATED_THRESHOLD = 0.70


def gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
