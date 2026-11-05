import os
import re
from random import sample

from fastapi import APIRouter, HTTPException, Request

from ..core.config import RELATED_THRESHOLD, gemini_model
from ..api.schemas import ChatRequest, FeedbackRequest
from ..domain.catalog import normalize_text
from ..llm.gemini import GeminiAPIError

router = APIRouter()
QUIZ_TERMS = {"quiz", "test", "اختبار", "الاختبار", "كويز", "الكويز", "امتحان", "الامتحان"}


def handover() -> dict:
    return {
        "label": "Ask a qualified Egyptian Sign Language instructor",
        "url": os.getenv("HUMAN_HANDOVER_URL") or None,
        "message": "For expert confirmation, consult a qualified Egyptian Sign Language instructor.",
    }


def response_with_trace(request: Request, response: dict, trace: dict, model_context: dict | None = None) -> dict:
    if model_context:
        phrase, model = request.app.state.gemini.generate_relevant_reply(**model_context)
        if phrase:
            response["model_reply"] = phrase
        elif model.get("reason") in {
            "HTTPStatusError",
            "TimeoutException",
            "ConnectError",
            "ConnectTimeout",
            "ReadTimeout",
            "WriteTimeout",
            "RemoteProtocolError",
            "InvalidModelResponse",
            "RepeatedOrInvalidModelResponse",
        }:
            system_issue = {"rule": "R6", "component": "Gemini", "error_type": model["reason"]}
            trace["system_issue"] = system_issue
            response["system_issue"] = system_issue
            response["system_warning"] = "تعذر توليد رد المساعد مؤقتًا، لكن نتيجة الإشارة الموثقة ما زالت متاحة. يمكنك إعادة المحاولة."
    else:
        model = {"used": False, "reason": "No verified sign match to contextualize"}
    trace["model"] = model
    response["trace_id"] = request.app.state.traces.add(trace)
    response["model"] = model
    return response


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
    catalog = request.app.state.catalog
    trace = {
        "input": payload.message,
        "normalized_input": normalize_text(payload.message),
        "model_version": gemini_model(),
    }
    normalized_input = trace["normalized_input"]
    input_terms = normalized_input.split()
    if QUIZ_TERMS.intersection(input_terms):
        trace.update({"result_type": "quiz_request", "rule": "QUIZ", "detected_intent": "quiz"})
        trace_id = request.app.state.traces.add(trace)
        return {
            "status": "quiz",
            "reply": "سأفتح لك الاختبار. شاهدي الفيديو واختاري معنى الإشارة.",
            "trace_id": trace_id,
        }

    if not re.search(r"[A-Za-z\u0600-\u06FF0-9]", payload.message) or len(input_terms) > 4:
        reason = "non_word_input" if not input_terms else "request_too_long"
        trace.update({
            "result_type": "out_of_scope",
            "rule": "R5",
            "detected_intent": "out_of_scope",
            "intent_reason": reason,
            "matched_entry": None,
        })
        return response_with_trace(request, {
            "status": "out_of_scope",
            "reply": "إشارة تساعدك في البحث عن كلمات أو عبارات قصيرة، أو بدء الاختبار. أرسل كلمة أو اكتب «اختبار».",
            "video_url": None,
            "handover": handover(),
        }, trace)

    sign, rule, matched_field, matched_value = catalog.find(payload.message)
    if sign is None:
        candidates = catalog.similarity_candidates(payload.message)
        related = [candidate for candidate in candidates if candidate["score"] >= RELATED_THRESHOLD]
        if related:
            visible_candidates = [{
                **candidate,
                "badge": "Related, not the same word",
                "reason": candidate["relation_note"] or "related but not the same word",
            } for candidate in related[:3]]
            trace.update({
                "result_type": "related",
                "rule": "R3",
                "threshold": RELATED_THRESHOLD,
                "scores": [{"entry_id": item["id"], "score": item["score"]} for item in visible_candidates],
                "entries": [{
                    "entry_id": item["id"],
                    "matched_term": item["matched_term"],
                    "relation_note": item["relation_note"],
                } for item in visible_candidates],
            })
            return response_with_trace(request, {
                "status": "related",
                "reply": "وجدنا كلمات قريبة في الكتابة، لكنها ليست نفس الكلمة. اختَر بحذر:",
                "related": visible_candidates,
                "threshold": RELATED_THRESHOLD,
                "handover": handover(),
            }, trace)

        best_candidate = candidates[0] if candidates else None
        suggested_examples = catalog.examples()
        trace.update({
            "result_type": "no_verified_match",
            "rule": "R4",
            "matched_entry": None,
            "searched_term": payload.message,
            "best_candidate": best_candidate,
            "best_score": best_candidate["score"] if best_candidate else 0.0,
            "threshold": RELATED_THRESHOLD,
            "suggested_examples": suggested_examples,
        })
        return response_with_trace(request, {
            "status": "not_found",
            "reply": (
                f'لا توجد مطابقة موثقة لعبارة "{payload.message}" في مجموعة البيانات. '
                "هذا لا يعني أن الإشارة غير موجودة. جرّب أحد الأمثلة أو اسأل مختصًا."
            ),
            "video_url": None,
            "handover": handover(),
            "searched_term": payload.message,
            "suggested_examples": suggested_examples,
            "best_candidate": best_candidate,
            "best_score": best_candidate["score"] if best_candidate else 0.0,
            "threshold": RELATED_THRESHOLD,
        }, trace)

    result_type = "exact_match" if rule == "R1" else "alias_match"
    trace.update({
        "result_type": result_type,
        "rule": rule,
        "matched_field": matched_field,
        "matched_alias": matched_value if rule == "R2" else None,
        "matched_entry": sign["id"],
        "video_url": catalog.video_url(sign),
        "score": None,
        "threshold": None,
    })
    return response_with_trace(request, {
        "status": "found",
        "result_label": "Exact match" if rule == "R1" else "Exact match (alternative word)",
        "reply": f'الإشارة المطلوبة: {sign["arabic"]}',
        "arabic": sign["arabic"],
        "english": sign["english"],
        "franco": sign["franco"],
        "video_url": catalog.video_url(sign),
    }, trace, {
        "result_type": result_type,
        "arabic": sign["arabic"],
        "english": sign["english"],
    })


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
    trace.setdefault("feedback", []).append({"rating": payload.rating, "reason": payload.reason})
    return {"status": "received", "message": "Thank you for helping improve Ishara."}


@router.get("/quiz")
def get_quiz_questions(request: Request):
    catalog = request.app.state.catalog
    questions = [{
        "id": sign["id"],
        "arabic": sign["arabic"],
        "english": sign["english"],
        "franco": sign["franco"],
        "video_url": catalog.video_url(sign),
    } for sign in sample(list(catalog.signs.values()), k=min(5, len(catalog.signs)))]
    return {"status": "success", "questions": questions}
