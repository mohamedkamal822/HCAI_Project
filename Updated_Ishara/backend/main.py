"""
CoMind / Ishara API (FastAPI).

Run from the backend folder:
    uvicorn main:app --reload
Then open frontend/index.html (for example with VS Code Live Server),
or open http://127.0.0.1:8000/app/ .
"""

import json
import random
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:                                   # optional: read HF_TOKEN from backend/.env
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from engine import ENGINE_VERSION, Engine, template_reply
import llm

# Project paths
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
DATASET_DIR = BASE_DIR / "dataset_selected_h264"
FRONTEND_DIR = BASE_DIR / "frontend"
LOG_DIR = BACKEND_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

engine = Engine()
TRACES = {}                            # trace_id -> trace (kept in memory for this session)

app = FastAPI(
    title="Ishara API",
    description="Backend for the CoMind / Ishara Egyptian Sign Language learning chatbot",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if DATASET_DIR.exists():
    app.mount("/videos", StaticFiles(directory=str(DATASET_DIR)), name="videos")
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="app")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def video_url(video_path: str) -> str:
    """'dataset_selected_h264/tmam/tmam_4092.mp4' -> '/videos/tmam/tmam_4092.mp4'"""
    parts = Path(video_path).parts
    if parts and parts[0].startswith("dataset_selected"):
        parts = parts[1:]
    return "/videos/" + quote("/".join(parts), safe="/")


def log_jsonl(name: str, record: dict):
    with open(LOG_DIR / name, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_response(trace: dict) -> dict:
    t0 = time.perf_counter()
    draft = template_reply(trace)
    reply, model_info = llm.phrase(trace, draft, engine)
    trace["template_reply"] = draft
    trace["reply"] = reply
    trace["reply_source"] = "model" if model_info["used"] else "template"
    trace["model"] = model_info
    trace["total_ms"] = round(trace["decision_ms"] + (time.perf_counter() - t0) * 1000, 1)

    results = []
    for r in trace.get("results", []):
        results.append({**r, "video_url": video_url(r["video"])})

    actions = []
    if trace["rule"] in ("R3", "R4", "R5"):
        actions += ["browse"]
    if trace["rule"] in ("R1", "R2", "R3"):
        actions += ["not_what_i_meant"]
    if trace["rule"] == "R0" and trace.get("intent") == "quiz":
        actions += ["open_quiz"]
    if trace["rule"] in ("R4", "R7"):
        actions += ["handover"]

    TRACES[trace["trace_id"]] = trace
    log_jsonl("traces.jsonl", trace)
    return {
        "status": "found" if trace["rule"] in ("R1", "R2") else
                  "related" if trace["rule"] == "R3" else "not_found",
        "rule": trace["rule"],
        "rule_name": trace["rule_name"],
        "badge": trace["badge"],
        "reply": reply,
        "language": trace["language"],
        "results": results,
        "actions": actions,
        "trace_id": trace["trace_id"],
        "trace": trace,
        # kept for the old frontend:
        "arabic": results[0]["arabic"] if results and trace["rule"] in ("R1", "R2") else None,
        "english": results[0]["english"] if results and trace["rule"] in ("R1", "R2") else None,
        "video_url": results[0]["video_url"] if results and trace["rule"] in ("R1", "R2") else None,
    }


def system_problem(message: str, lang: str, err: Exception) -> dict:
    trace = {
        "trace_id": "err" + str(int(time.time() * 1000))[-9:],
        "input": message, "language": lang, "rule": "R6",
        "rule_name": "System problem", "badge": {"icon": "!", "text": "System problem"},
        "error_type": type(err).__name__, "results": [], "checks": [], "candidates": [],
        "settings": {}, "decision_ms": 0,
    }
    reply = template_reply(trace)
    log_jsonl("errors.jsonl", {**trace, "error": str(err)})
    return {"status": "error", "rule": "R6", "rule_name": "System problem", "badge": trace["badge"],
            "reply": reply, "language": lang, "results": [], "actions": ["retry", "edit", "start_over"],
            "trace_id": trace["trace_id"], "trace": trace}


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=300)
    exact_only: bool = False
    lang: Optional[str] = Field(default=None, pattern="^(ar|en)$")   # language of the website; replies follow it
    simulate_error: bool = False       # for testing the R6 path in the demo/evaluation


class AlternativesRequest(BaseModel):
    trace_id: str
    lang: Optional[str] = Field(default=None, pattern="^(ar|en)$")


class FeedbackRequest(BaseModel):
    trace_id: str
    vote: str = Field(pattern="^(up|down)$")
    reason: Optional[str] = None       # wrong sign, wrong word, hard to see, unclear explanation, other
    comment: Optional[str] = Field(default=None, max_length=300)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Ishara API!",
        "status": "running",
        "total_signs": len(engine.signs),
        "engine_version": ENGINE_VERSION,
        "model": llm.MODEL_ID,
        "model_enabled": llm.model_enabled(),
        "prompt_version": llm.PROMPT_VERSION,
        "threshold": engine.threshold,
    }


@app.get("/signs")
def list_signs():
    """All verified words, for the 'Browse verified words' list."""
    items = [{"id": sid, "arabic": e["arabic"], "english": e["english"]} for sid, e in engine.signs.items()]
    return {"count": len(items), "signs": sorted(items, key=lambda x: x["english"].casefold())}


@app.post("/chat")
def chat(request: ChatRequest):
    lang = "ar" if any("؀" <= c <= "ۿ" for c in request.message) else "en"
    try:
        if request.simulate_error:
            raise TimeoutError("Simulated timeout (test of the R6 path)")
        trace = engine.decide(request.message, exact_only=request.exact_only, reply_lang=request.lang)
        return build_response(trace)
    except Exception as err:
        return JSONResponse(system_problem(request.message, lang, err), status_code=200)


@app.post("/alternatives")
def alternatives(request: AlternativesRequest):
    """'This isn't what I meant': search again without the entries already shown."""
    old = TRACES.get(request.trace_id)
    if old is None:
        raise HTTPException(404, "Trace not found. Please search again.")
    shown = [r["id"] for r in old.get("results", [])]
    word = old.get("extracted_word") or old.get("normalized") or old["input"]
    trace = engine.decide(word, exact_only=False, exclude=shown, reply_lang=request.lang or old.get("language"))
    trace["alternative_to"] = request.trace_id
    trace["excluded_entries"] = shown
    if trace["rule"] in ("R1", "R2"):            # cannot happen once excluded, but stay safe
        trace["rule"], trace["rule_name"] = "R3", "Related, not the same word"
    return build_response(trace)


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    trace = TRACES.get(trace_id)
    if trace is None:
        raise HTTPException(404, "Trace not found")
    return trace


@app.post("/feedback")
def feedback(request: FeedbackRequest):
    trace = TRACES.get(request.trace_id, {})
    record = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trace_id": request.trace_id,
        "vote": request.vote,
        "reason": request.reason,
        "comment": request.comment,
        "input": trace.get("input"),
        "rule": trace.get("rule"),
        "entries": [r["id"] for r in trace.get("results", [])],
    }
    log_jsonl("feedback.jsonl", record)
    return {"status": "saved", "message": "Thank you. The team reviews feedback every week."}


@app.get("/quiz")
def get_quiz_questions(n: int = 5, seed: Optional[int] = None):
    """Questions are built by code: the right answer and 3 distractors all come from the index."""
    rng = random.Random(seed)
    ids = list(engine.signs)
    chosen = rng.sample(ids, k=min(n, len(ids)))
    questions = []
    for sid in chosen:
        e = engine.signs[sid]
        distractors = rng.sample([i for i in ids if i != sid], 3)
        options = [sid] + distractors
        rng.shuffle(options)
        questions.append({
            "id": sid,
            "arabic": e["arabic"],
            "english": e["english"],
            "franco": e["franco"],
            "video_url": video_url(e["video"]),
            "options": [{"id": o, "arabic": engine.signs[o]["arabic"],
                         "english": engine.signs[o]["english"]} for o in options],
            "source": f"Dataset entry \"{sid}\" (Egyptian Sign Language Recognition, Kaggle)",
        })
    return {"status": "success", "questions": questions}
