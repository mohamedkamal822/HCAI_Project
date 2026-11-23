import re
import time
from ..core.config import RELATED_THRESHOLD
from ..domain.catalog import normalize_text


RULE_NAMES = {
    "R0": "Greeting, help or quiz request",
    "R1": "Exact match",
    "R2": "Exact match (alternative word)",
    "R3": "Related, not the same word",
    "R4": "No verified match",
    "R5": "Out of scope",
    "R6": "System problem",
    "R7": "Safety: handed over or refused",
}
BADGES = {
    "R0": {"icon": "i", "text": "Info"},
    "R1": {"icon": "✓", "text": "Exact match"},
    "R2": {"icon": "✓", "text": "Exact match (alternative word)"},
    "R3": {"icon": "≈", "text": "Related, not the same word"},
    "R4": {"icon": "∅", "text": "No verified match"},
    "R5": {"icon": "?", "text": "Out of scope"},
    "R6": {"icon": "!", "text": "System problem"},
    "R7": {"icon": "⚠", "text": "Needs a person"},
}
GREETING = {"hi", "hello", "hey", "مرحبا", "اهلا", "اهلا بيك", "السلام عليكم", "سلام", "hii", "ازيك يا ishara"}
HELP = {"help", "مساعده", "مساعدة", "ساعدني", "what can you do", "who are you", "انت مين", "بتعمل ايه", "what is this", "ايه ده", "start", "ابدا"}
QUIZ = {"quiz", "test me", "start quiz", "practice", "اختبار", "امتحان", "اختبرني", "امتحني", "كويز", "تدريب"}
EMERGENCY = re.compile(r"(suicide|kill myself|end my life|hurt myself|emergency|انتحار|اقتل نفسي|انهي حياتي|عايز اموت|عاوز اموت|اموت نفسي|طوارئ|اسعاف|حد بيموت|in danger)", re.I)
INTERPRET = re.compile(r"(interpret|interpreter|translate (?:for|a|the|this|my) (?:conversation|meeting|doctor|hospital|court|call)|مترجم|ترجم(?:لي)? (?:محادثه|محادثة|كلام|مكالمه|مكالمة)|(?:hospital|court|police|lawyer|surgery|مستشفي|المستشفي|محكمه|المحكمه|محكمة|قسم|محامي|عمليه).*(?:sign|اشاره|اشارة|اصم|deaf)|(?:sign|اشاره|اشارة|اصم|deaf).*(?:hospital|court|police|lawyer|surgery|مستشفي|المستشفي|محكمه|محكمة|المحكمه|محامي))", re.I)
ABUSE = re.compile(r"((?:insult|mock|offend|bully|curse at|swear at|make fun of|humiliate) (?:him|her|them|someone|somebody|my|a |the |deaf|people)|bad words|swear words|curse words|rude signs?|offensive signs?|(?:اشتم|اهين|اتريق علي|اضايق) (?:حد|زميلي|زميلتي|صاحبي|واحد|الاصم|الصم|ه|ها)|شتايم|شتيمه|شتيمة|الفاظ وحشه|كلام وحش)", re.I)
PHONE = re.compile(r"(?:\+?\d[\d\s-]{7,}\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
OUT_OF_SCOPE = re.compile(r"(weather|news|joke|recipe|homework|code|python|football|match|price|طقس|الجو|اخبار|نكته|نكتة|وصفه|واجب|كوره|ماتش|سعر)", re.I)
LOOKUP_PATTERNS = [
    re.compile(r"^(?:how (?:do|can|would) (?:i|you|we) (?:say|sign|show) )(.+?)(?: in (?:egyptian )?sign(?: language)?| in esl)?$"),
    re.compile(r"^(?:how to (?:say|sign) )(.+?)(?: in (?:egyptian )?sign(?: language)?| in esl)?$"),
    re.compile(r"^(?:what(?:'s| is) the sign for |sign for |the sign for |show me the sign for |show me |teach me )(.+)$"),
    re.compile(r"^(?:ازاي|كيف|ازاى) (?:اقول|اعمل|نقول|تقول|اشاور) (.+?)(?: بالاشاره| بالاشارة| بلغه الاشاره| بلغة الاشارة| بالاشارات)?$"),
    re.compile(r"^(?:اشاره|اشارة|الاشاره|الاشارة|علامه|علامة) (?:كلمه |كلمة )?(.+)$"),
    re.compile(r"^(?:عايز اتعلم|عاوز اتعلم|علمني|وريني) (?:اشاره |اشارة |كلمه |كلمة )?(.+)$"),
]
TEMPLATE_EXAMPLES = {
    "ar": "صباح الخير، دكتور، عامل إيه، كتاب",
    "en": "Good morning, Doctor, How are you, Book",
}


def handover() -> dict:
    import os

    return {
        "label": "Ask a qualified Egyptian Sign Language instructor",
        "url": os.getenv("HUMAN_HANDOVER_URL") or None,
        "message": "For expert confirmation, consult a qualified Egyptian Sign Language instructor.",
    }


def _language(text: str, preferred: str | None) -> str:
    if preferred in {"ar", "en"}:
        return preferred
    return "ar" if re.search(r"[\u0600-\u06ff]", text) else "en"


def _trace(message: str, language: str, exact_only: bool) -> dict:
    return {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "engine_version": "ishara-modular-r0-r7",
        "input": message,
        "language": language,
        "input_language": _language(message, None),
        "normalized": "",
        "normalization_steps": [],
        "settings": {"exact_matches_only": exact_only},
        "threshold": RELATED_THRESHOLD,
        "similarity_method": "difflib character ratio",
        "dataset": "Egyptian Sign Language Recognition, 56 indexed words",
        "checks": [],
        "candidates": [],
        "results": [],
    }


def _check(trace: dict, name: str, outcome: str, detail: str = "") -> None:
    trace["checks"].append({"check": name, "outcome": outcome, "detail": detail})


def _entry_view(catalog, sign: dict, language: str, score=None, reason=None) -> dict:
    note = catalog.entry_note(sign["id"]) or {}
    return {
        "id": sign["id"],
        "arabic": sign["arabic"],
        "english": sign["english"],
        "franco": sign.get("franco", ""),
        "video": sign["video"],
        "video_url": catalog.video_url(sign),
        "score": score,
        "reason": reason,
        "note": note.get(language) or note.get("en") or None,
    }


def _template(rule: str, language: str, trace: dict) -> str:
    arabic = language == "ar"
    results = trace.get("results") or []
    first = results[0] if results else {}
    if rule in {"R1", "R2"}:
        if arabic:
            alt = " بطريقة بديلة راجعها فريقنا" if rule == "R2" else ""
            return f"دي إشارة «{first.get('arabic', '')}» الموثقة{alt}. شاهد الفيديو واتمرّن عليها."
        alt = " (found through a team-reviewed alternative word)" if rule == "R2" else ""
        return f'This is the verified sign for "{first.get("english", "")}"{alt}. Watch the video and practise it.'
    if rule == "R3":
        labels = "، ".join(f"«{item['arabic']}»" for item in results) if arabic else ", ".join(f"“{item['english']}”" for item in results)
        return (f"الكلمات دي قريبة في الكتابة لكنها مش نفس كلمتك: {labels}." if arabic
                else f"These entries look similar, but they are not the same word: {labels}.")
    if rule == "R4":
        searched = trace.get("extracted_word") or trace.get("normalized") or trace.get("input", "")
        if trace.get("settings", {}).get("exact_matches_only"):
            extra_ar, extra_en = " الكلمات القريبة مخفية من الإعدادات.", " Related words are hidden by your setting."
        else:
            extra_ar = extra_en = ""
        return (f"ملقيتش إشارة موثقة لـ«{searched}» في مجموعتنا. ده مش معناه إن الإشارة مش موجودة. جرّب كلمة تانية مثل {TEMPLATE_EXAMPLES['ar']} أو اسأل مختصًا.{extra_ar}"
                if arabic else f'I could not find a verified sign for "{searched}" in our catalog. That does not mean the sign does not exist. Try {TEMPLATE_EXAMPLES["en"]} or ask a qualified instructor.{extra_en}')
    if rule == "R0":
        if trace.get("intent") == "quiz":
            return "يلا بينا! افتح الاختبار وتمرّن على الإشارات بالفيديو." if arabic else "Open the quiz to practise reading signs from videos."
        return ("أهلاً بيك! أنا إشارة، مساعد تعليمي بيعرض فيديوهات موثقة من مجموعة كلمات محدودة. اكتب كلمة بالعربي أو الإنجليزي، ومش بترجم محادثات."
                if arabic else "Hi! I'm Ishara, a learning assistant that shows verified sign videos from a limited catalog. Search a word in Arabic or English; I cannot interpret conversations.")
    if rule == "R5":
        return ("أنا بساعدك تبحث عن إشارات كلمات أو عبارات قصيرة في لغة الإشارة المصرية، أو تجرّب الاختبار."
                if arabic else "I help look up short words or phrases in Egyptian Sign Language, or you can try the quiz.")
    if rule == "R7":
        safety = trace.get("safety")
        if safety == "emergency":
            return ("لو إنت أو حد تاني في خطر، كلم الإسعاف ١٢٣ أو الشرطة ١٢٢ فورًا، أو تواصل مع شخص تثق به. أنا أداة تعليمية ومش بديل للطوارئ."
                    if arabic else "If you or someone else is in immediate danger in Egypt, call ambulance 123 or police 122 now, or contact someone you trust. Ishara is a learning tool, not emergency support.")
        if safety == "interpretation":
            return ("للمواقف الطبية أو القانونية، استعِن بمترجم مؤهل للغة الإشارة المصرية. أنا بعرض إشارات كلمات منفردة ومش بترجم محادثات."
                    if arabic else "For medical or legal conversations, contact a qualified Egyptian Sign Language interpreter. Ishara shows individual words and cannot interpret conversations.")
        if safety == "abuse":
            return ("مش هقدر أساعد في إشارات هدفها إهانة أو إيذاء شخص. تقدر تبحث عن كلمة منفردة للتعلم."
                    if arabic else "I can’t help with signs intended to insult or hurt someone. You can still look up an individual word for learning.")
        return ("تم إخفاء رقم الهاتف أو البريد الإلكتروني من رسالتك. من فضلك ما تشاركش بيانات شخصية هنا."
                if arabic else "I removed the phone number or email from your message. Please do not share personal details here.")
    if rule == "R6":
        return "حصلت مشكلة مؤقتة. حاول مرة أخرى أو عدّل الكلمة." if arabic else "Something went wrong temporarily. Please try again or edit your word."
    return "اكتب كلمة للبحث." if arabic else "Type a word to search."


def _finish(request, trace: dict, rule: str, actions: list[str], model_context: dict | None = None) -> dict:
    trace["rule"] = rule
    trace["rule_name"] = RULE_NAMES[rule]
    trace["badge"] = BADGES[rule]
    trace["actions"] = actions
    trace["model"] = {"used": False, "model": None, "status": "template response"}
    reply = _template(rule, trace["language"], trace)
    model_reply = None
    if model_context and rule in {"R1", "R2", "R3", "R4"}:
        model_reply, model = request.app.state.gemini.generate_relevant_reply(**model_context)
        trace["model"] = model
        if model_reply:
            reply = model_reply
    trace["reply_source"] = "model" if model_reply else "template"
    trace["reply"] = reply
    trace["total_ms"] = round((time.perf_counter() - trace.pop("_started_at")) * 1000, 1)
    trace_id = request.app.state.traces.add(trace)
    request.app.state.audit_log.append("traces.jsonl", trace)
    status = {
        "R0": "info", "R1": "found", "R2": "found", "R3": "related",
        "R4": "not_found", "R5": "out_of_scope", "R6": "error", "R7": "safety",
    }[rule]
    result = {
        "status": status,
        "rule": rule,
        "rule_name": trace["rule_name"],
        "badge": trace["badge"],
        "reply": reply,
        "language": trace["language"],
        "results": trace.get("results", []),
        "actions": actions,
        "trace_id": trace_id,
        "trace": trace,
        "model": trace["model"],
        "model_reply": model_reply,
    }
    if trace.get("intent") == "quiz":
        result["intent"] = "quiz"
    if trace.get("rule") in {"R1", "R2"} and trace.get("results"):
        first = trace["results"][0]
        result.update({
            "result_label": trace["badge"]["text"],
            "arabic": first["arabic"],
            "english": first["english"],
            "franco": first.get("franco"),
            "video_url": first["video_url"],
        })
    if rule in {"R4", "R7"}:
        result["handover"] = handover()
    return result


def handle_chat(request, payload) -> dict:
    if payload.simulate_error:
        return system_problem(request, payload.message, TimeoutError("Simulated timeout"))

    return handle_message(
        request,
        payload.message,
        exact_only=payload.exact_only,
        reply_language=payload.lang,
    )


def handle_message(request, message: str, exact_only: bool = False, reply_language: str | None = None,
                   excluded: set[str] | None = None) -> dict:
    started = time.perf_counter()
    language = _language(message, reply_language)
    catalog = request.app.state.catalog
    trace = _trace(message, language, exact_only)
    trace["_started_at"] = started
    excluded = excluded or set()

    masked = EMAIL.sub("[email removed]", PHONE.sub("[number removed]", message))
    if masked != message:
        trace["input"] = masked
        trace["normalized"] = normalize_text(masked)
        _check(trace, "Personal data filter", "found", "A phone number or email was removed before processing.")
        trace["safety"] = "privacy"
        return _finish(request, trace, "R7", ["handover"])

    normalized = normalize_text(message)
    trace["normalized"] = normalized
    _check(trace, "Personal data filter", "none found")
    if not normalized:
        _check(trace, "Input check", "empty after normalization")
        return _finish(request, trace, "R5", ["browse"])

    hit = catalog.find(message)
    _check(trace, "Exact lookup on full input", "match" if hit else "no match")
    if hit and hit[0] and hit[0]["id"] not in excluded:
        sign, rule, matched_field, matched_value = hit
        result = _entry_view(catalog, sign, language, score=1.0)
        trace["results"] = [result]
        trace["matched_field"] = matched_field
        trace["matched_text"] = matched_value
        trace["extracted_word"] = normalized
        trace["threshold"] = RELATED_THRESHOLD
        model_context = {
            "rule": rule, "language": language,
            "results": [{"arabic": result["arabic"], "english": result["english"]}],
            "query": trace.get("extracted_word") or trace.get("normalized", ""),
        }
        return _finish(request, trace, rule, ["not_what_i_meant"], model_context)

    if EMERGENCY.search(normalized):
        _check(trace, "Safety: emergency or self-harm", "detected")
        trace["safety"] = "emergency"
        return _finish(request, trace, "R7", ["handover"])
    if INTERPRET.search(normalized):
        _check(trace, "Safety: high-stakes interpretation request", "detected")
        trace["safety"] = "interpretation"
        return _finish(request, trace, "R7", ["handover"])
    if ABUSE.search(normalized):
        _check(trace, "Safety: request to insult or hurt someone", "detected")
        trace["safety"] = "abuse"
        return _finish(request, trace, "R7", [])

    extracted = None
    for pattern in LOOKUP_PATTERNS:
        match = pattern.match(normalized)
        if match:
            extracted = match.group(1).strip()
            break
    if extracted:
        trace["extracted_word"] = extracted
        _check(trace, "Lookup phrase", "found", f'The word to look up is "{extracted}".')
        hit = catalog.find(extracted)
        _check(trace, "Exact lookup on extracted word", "match" if hit else "no match")
        if hit and hit[0] and hit[0]["id"] not in excluded:
            sign, rule, matched_field, matched_value = hit
            result = _entry_view(catalog, sign, language, score=1.0)
            trace["results"] = [result]
            trace["matched_field"] = matched_field
            trace["matched_text"] = matched_value
            model_context = {
                "rule": rule, "language": language,
                "results": [{"arabic": result["arabic"], "english": result["english"]}],
                "query": extracted,
            }
            return _finish(request, trace, rule, ["not_what_i_meant"], model_context)
        normalized = extracted
        trace["normalized"] = normalized

    if normalized in GREETING or normalized in HELP:
        _check(trace, "Intent", "greeting or help")
        trace["intent"] = "help"
        return _finish(request, trace, "R0", [])
    if normalized in QUIZ:
        _check(trace, "Intent", "quiz")
        trace["intent"] = "quiz"
        return _finish(request, trace, "R0", ["open_quiz"])

    confusable = catalog.confusable(normalized)
    if confusable and not exact_only:
        sign = catalog.signs.get(confusable.get("entry"))
        if sign:
            note = confusable.get(language) or confusable.get("en") or "related but not the same word"
            result = _entry_view(catalog, sign, language, reason=note)
            trace["confusable"] = True
            trace["results"] = [result]
            trace["candidates"] = [{
                "id": sign["id"], "label": f'{sign["english"]} · {sign["arabic"]}',
                "score": None, "decision": "shown as related", "reason": "Team-written confusable note",
            }]
            _check(trace, "Confusable word list", "match", note)
            return _finish(request, trace, "R3", ["browse", "not_what_i_meant"])

    _check(trace, "Safety checks", "passed")
    words = normalized.split()
    if OUT_OF_SCOPE.search(normalized) or len(words) > 4:
        _check(trace, "Scope check", "out of scope", "Topic is not a short sign lookup.")
        return _finish(request, trace, "R5", ["browse"])
    _check(trace, "Scope check", "in scope", f"{len(words)} word(s)")

    candidates = catalog.similarity_candidates(normalized, limit=5)
    for candidate in candidates:
        if candidate["id"] in excluded:
            continue
        decision = "not shown" if exact_only else (
            "shown as related" if candidate["score"] >= RELATED_THRESHOLD else "rejected"
        )
        reason = "Exact matches only is on" if exact_only else (
            f"score {candidate['score']} ≥ T {RELATED_THRESHOLD}" if candidate["score"] >= RELATED_THRESHOLD
            else f"score {candidate['score']} < T {RELATED_THRESHOLD}"
        )
        candidate["decision"] = decision
        candidate["reason"] = reason
        candidate["label"] = f'{candidate["english"]} · {candidate["arabic"]}'
    trace["candidates"] = candidates
    related_candidates = [candidate for candidate in candidates if candidate["decision"] == "shown as related"][:3]
    if related_candidates:
        for candidate in related_candidates:
            sign = catalog.signs[candidate["id"]]
            note = candidate.get("relation_note")
            if language == "ar":
                reason = (f'الكلمة مكتوبة شبه «{candidate["matched_term"]}» بنسبة {round(candidate["score"] * 100)}%، '
                          f'ومعناها في الداتا «{sign["arabic"]}». دي كلمة مختلفة عن اللي كتبتها.')
            else:
                reason = (f'Spelling is similar to "{candidate["matched_term"]}" '
                          f'({candidate["score"]:.0%}; threshold {RELATED_THRESHOLD:.0%}). '
                          f'The catalog entry means "{sign["english"]}" ({sign["arabic"]}); it is not the word you typed.')
            if note:
                reason += " " + note
            result = _entry_view(catalog, sign, language, score=candidate["score"], reason=reason)
            trace["results"].append(result)
        model_context = {
            "rule": "R3", "language": language,
            "results": [{"arabic": item["arabic"], "english": item["english"]} for item in trace["results"]],
            "query": normalized,
        }
        return _finish(request, trace, "R3", ["browse", "not_what_i_meant"], model_context)

    best = candidates[0] if candidates else None
    if best:
        trace["best_candidate"] = {
            "id": best["id"], "label": best["label"], "score": best["score"],
        }
    model_context = {"rule": "R4", "language": language, "results": [], "query": normalized}
    return _finish(request, trace, "R4", ["browse", "handover"], model_context)


def system_problem(request, message: str, error: Exception) -> dict:
    language = _language(message, None)
    trace = _trace(message, language, False)
    trace["rule"] = "R6"
    trace["error_type"] = type(error).__name__
    trace["system_error"] = True
    trace["checks"].append({"check": "System", "outcome": "error", "detail": type(error).__name__})
    trace["_started_at"] = time.perf_counter()
    result = _finish(request, trace, "R6", ["retry", "edit", "start_over"])
    request.app.state.audit_log.append("errors.jsonl", trace)
    return result


def handle_alternatives(request, trace_id: str, language: str | None = None) -> dict:
    trace = request.app.state.traces.get(trace_id)
    if trace is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trace not found or expired.")
    excluded = {item["id"] for item in trace.get("results", [])}
    searched = trace.get("extracted_word") or trace.get("normalized") or trace.get("input", "")
    return handle_message(request, searched, reply_language=language or trace.get("language"), excluded=excluded)


def public_signs(request) -> dict:
    catalog = request.app.state.catalog
    signs = [
        {"id": sid, "arabic": sign["arabic"], "english": sign["english"], "franco": sign.get("franco", "")}
        for sid, sign in catalog.signs.items()
    ]
    signs.sort(key=lambda item: item["english"].casefold())
    return {"count": len(signs), "signs": signs}


def feedback_record(request, trace_id: str, vote: str, reason: str | None) -> dict:
    trace = request.app.state.traces.get(trace_id) or {}
    record = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trace_id": trace_id,
        "vote": vote,
        "reason": reason,
        "input": trace.get("input"),
        "rule": trace.get("rule"),
        "entries": [item["id"] for item in trace.get("results", [])],
    }
    request.app.state.audit_log.append("feedback.jsonl", record)
    if trace:
        trace.setdefault("feedback", []).append({"vote": vote, "reason": reason})
    return {"status": "saved", "message": "Thank you. The team reviews feedback every week."}
