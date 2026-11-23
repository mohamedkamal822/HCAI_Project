from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .app.api.routes import router
from .app.core.config import FRONTEND_DIR, LOGS_DIR, MAX_TRACES, SIGNS_PATH, VIDEOS_DIR
from .app.domain.catalog import SignCatalog
from .app.llm.gemini import GeminiService
from .app.services.traces import TraceStore
from .app.services.audit_log import JsonlAuditLog


app = FastAPI(
    title="Ishara API",
    description="Backend for the Ishara Sign Language Learning Chatbot",
    version="1.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.catalog = SignCatalog(SIGNS_PATH)
app.state.traces = TraceStore(MAX_TRACES)
app.state.audit_log = JsonlAuditLog(LOGS_DIR)
app.state.gemini = GeminiService()
app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")
app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def chat_validation_handler(request: Request, error: RequestValidationError):
    if request.url.path != "/chat":
        return JSONResponse(status_code=422, content={"detail": "The request did not match the expected format."})

    body = error.body if isinstance(error.body, dict) else {}
    input_text = body.get("message", "")
    trace = {
        "rule": "R5",
        "rule_name": "Out of scope",
        "badge": {"icon": "?", "text": "Out of scope"},
        "result_type": "out_of_scope",
        "input": input_text,
        "detected_intent": "invalid_chat_input",
        "intent_reason": "validation_error",
        "validation_error_types": [item.get("type", "invalid") for item in error.errors()],
    }
    trace_id = app.state.traces.add(trace)
    return JSONResponse(
        status_code=422,
        content={
            "status": "out_of_scope",
            "rule": "R5",
            "reply": "أرسل كلمة أو عبارة قصيرة للبحث، أو اكتب «اختبار» لبدء الاختبار.",
            "rule_name": "Out of scope",
            "badge": {"icon": "?", "text": "Out of scope"},
            "language": "ar",
            "results": [],
            "actions": ["browse"],
            "trace": trace,
            "trace_id": trace_id,
        },
        headers={"Access-Control-Allow-Origin": "*"},
    )


@app.exception_handler(Exception)
async def system_error_handler(request: Request, error: Exception):
    trace = {
        "rule": "R6",
        "result_type": "system_error",
        "route": request.url.path,
        "error_type": type(error).__name__,
        "detected_intent": "system_failure",
    }
    trace_id = app.state.traces.add(trace)
    app.state.audit_log.append("errors.jsonl", {**trace, "trace_id": trace_id})
    return JSONResponse(
        status_code=503,
        content={
            "status": "system_error",
            "rule": "R6",
            "rule_name": "System problem",
            "badge": {"icon": "!", "text": "System problem"},
            "reply": "واجهنا مشكلة مؤقتة. حاول مرة أخرى بعد قليل.",
            "language": "ar",
            "results": [],
            "actions": ["retry", "edit", "start_over"],
            "trace": trace,
            "error_type": type(error).__name__,
            "trace_id": trace_id,
            "retryable": True,
        },
        headers={"Access-Control-Allow-Origin": "*"},
    )
