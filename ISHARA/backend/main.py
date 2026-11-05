from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .app.api.routes import router
from .app.core.config import MAX_TRACES, SIGNS_PATH, VIDEOS_DIR
from .app.domain.catalog import SignCatalog
from .app.llm.gemini import GeminiService
from .app.services.traces import TraceStore


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
app.state.gemini = GeminiService()
app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def chat_validation_handler(request: Request, error: RequestValidationError):
    if request.url.path != "/chat":
        return JSONResponse(status_code=422, content={"detail": "The request did not match the expected format."})

    body = error.body if isinstance(error.body, dict) else {}
    input_text = body.get("message", "")
    trace = {
        "rule": "R5",
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
    return JSONResponse(
        status_code=503,
        content={
            "status": "system_error",
            "rule": "R6",
            "reply": "واجهنا مشكلة مؤقتة. حاول مرة أخرى بعد قليل.",
            "error_type": type(error).__name__,
            "trace_id": trace_id,
            "retryable": True,
        },
        headers={"Access-Control-Allow-Origin": "*"},
    )
