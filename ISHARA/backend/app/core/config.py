import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(PROJECT_DIR / ".env")

SIGNS_PATH = BACKEND_DIR / "signs.json"
VIDEOS_DIR = PROJECT_DIR / "dataset_selected_h264"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_TRACES = 200
RELATED_THRESHOLD = 0.72


def gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
