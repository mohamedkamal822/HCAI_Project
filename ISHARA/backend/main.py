
import json
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset_selected_h264"
JSON_PATH = Path(__file__).resolve().parent / "signs.json"


# Load sign language data
with open(JSON_PATH, "r", encoding="utf-8") as file:
    signs = json.load(file)


app = FastAPI(
    title="Ishara API",
    description="Backend for the Ishara Sign Language Learning Chatbot",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve sign videos
app.mount(
    "/videos",
    StaticFiles(directory=str(DATASET_DIR)),
    name="videos"
)


# Request format
class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


# Normalize user input
def normalize_text(text):
    return " ".join(text.strip().casefold().split())


# Search for a sign
def find_sign(message):

    search_term = normalize_text(message)

    for sign in signs.values():

        searchable_values = [
            sign["franco"],
            sign["arabic"],
            sign["english"],
            *sign.get("aliases", [])
        ]

        for value in searchable_values:

            if value and normalize_text(value) == search_term:
                return sign

    return None


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Ishara API!",
        "status": "running",
        "total_signs": len(signs)
    }


# Chat endpoint

@app.post("/chat")
def chat(request: ChatRequest):

    sign = find_sign(request.message)

    # Sign not found
    if sign is None:
        return {
            "status": "not_found",
            "reply": (
                f'لم نجد إشارة موثقة لكلمة "{request.message}". '
                "جربي كلمة أخرى."
            ),
            "video_url": None
        }

    # Build video URL
    video_path = Path(sign["video"]).relative_to("dataset_selected")
    video_path = quote(video_path.as_posix(), safe="/")

    video_url = f"/videos/{video_path}"

    return {
        "status": "found",
        "reply": f'الإشارة المطلوبة: {sign["arabic"]}',
        "arabic": sign["arabic"],
        "english": sign["english"],
        "franco": sign["franco"],
        "video_url": video_url
    }


@app.get("/quiz")
def get_quiz_questions():

    selected_words = [
        "bsor3a",
        "mashy",
        "tmam",
        "flos",
        "whashny"
    ]

    quiz_questions = []

    for word in selected_words:
        sign = signs[word]

        video_path = Path(sign["video"]).relative_to("dataset_selected")
        video_path = quote(video_path.as_posix(), safe="/")

        quiz_questions.append({
            "id": sign["id"],
            "arabic": sign["arabic"],
            "english": sign["english"],
            "franco": sign["franco"],
            "video_url": f"/videos/{video_path}"
        })

    return {
        "status": "success",
        "questions": quiz_questions
    }
