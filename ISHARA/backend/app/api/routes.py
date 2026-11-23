import os
import random

from fastapi import APIRouter, HTTPException, Request

from ..api.schemas import AlternativesRequest, ChatRequest, FeedbackRequest
from ..llm.gemini import GeminiAPIError
from ..services.conversation import (
    feedback_record,
    handle_alternatives,
    handle_chat,
    public_signs,
)

router = APIRouter()


@router.get("/")
def home(request: Request):
    return {
        "message": "Welcome to Ishara API!",
        "status": "running",
        "total_signs": len(request.app.state.catalog.signs),
        "model_configured": bool(os.getenv("GEMINI_API_KEY")),
    }


@router.get("/models")
def available_models(request: Request, query: str = ""):
    try:
        return {"models": request.app.state.gemini.list_models(query)}
    except GeminiAPIError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.post("/chat")
def chat(request: Request, payload: ChatRequest):
    return handle_chat(request, payload)


@router.post("/alternatives")
def alternatives(request: Request, payload: AlternativesRequest):
    return handle_alternatives(request, payload.trace_id, payload.lang)


@router.get("/signs")
def list_signs(request: Request):
    return public_signs(request)


@router.get("/trace/{trace_id}")
def get_trace(request: Request, trace_id: str):
    trace = request.app.state.traces.get(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found or expired.")
    return trace


@router.post("/feedback")
def feedback(request: Request, payload: FeedbackRequest):
    trace = request.app.state.traces.get(payload.trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found or expired.")
    return feedback_record(request, payload.trace_id, payload.vote or payload.rating, payload.reason)


@router.get("/quiz")
def get_quiz_questions(request: Request, n: int = 5, seed: int | None = None):
    catalog = request.app.state.catalog
    ids = list(catalog.signs)
    rng = random.Random(seed)
    chosen = rng.sample(ids, k=min(max(n, 1), len(ids)))
    questions = []
    for sign_id in chosen:
        sign = catalog.signs[sign_id]
        options = [sign_id, *rng.sample([item for item in ids if item != sign_id], min(3, len(ids) - 1))]
        rng.shuffle(options)
        questions.append({
            "id": sign_id,
            "arabic": sign["arabic"],
            "english": sign["english"],
            "franco": sign.get("franco", ""),
            "video_url": catalog.video_url(sign),
            "options": [{"id": option, "arabic": catalog.signs[option]["arabic"],
                         "english": catalog.signs[option]["english"]} for option in options],
            "source": f'Dataset entry "{sign_id}" (Egyptian Sign Language Recognition)',
        })
    return {"status": "success", "questions": questions}
