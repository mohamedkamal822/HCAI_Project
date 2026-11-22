"""
Language-model layer (Qwen2.5-7B-Instruct through Hugging Face Inference Providers).

The model ONLY rewrites the reply sentence in a friendly way. It receives the
decision trace facts, never chooses a video, and never changes the rule.
A validator checks the model's text against the trace. If the check fails,
the model is off, or the call times out, the fixed template text is used.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request

from engine import normalize

MODEL_ID = os.getenv("COMIND_MODEL", "Qwen/Qwen2.5-7B-Instruct")
API_URL = os.getenv("COMIND_MODEL_URL", "https://router.huggingface.co/v1/chat/completions")
TIMEOUT_S = float(os.getenv("COMIND_MODEL_TIMEOUT", "8"))
PROMPT_VERSION = "phrasing-prompt-v1"
PHRASED_RULES = {"R1", "R2", "R3", "R4"}   # safety, scope and system messages stay fixed

SYSTEM_PROMPT = """You rewrite one chatbot reply for CoMind, a tool that shows Egyptian Sign Language videos from a fixed dataset.
Rules:
- Write at most 2 short, warm sentences in the language given by "language" (ar = Egyptian Arabic, en = English).
- Use ONLY the facts in FACTS. Do not add meanings, signs, examples, numbers or links that are not in FACTS.
- Copy every label in "must_mention" exactly as written.
- Never say a related entry is the same word. Never say a sign exists when result is "no verified match".
- Do not describe how to perform the sign.
Return only the reply text."""


def _token():
    return os.getenv("HF_TOKEN", "").strip()


def model_enabled():
    return bool(_token()) and os.getenv("COMIND_USE_MODEL", "1") != "0"


def facts_from_trace(trace):
    res = trace.get("results") or []
    facts = {
        "language": trace["language"],
        "result": trace["rule_name"],
        "user_typed": trace.get("extracted_word") or trace["input"],
        "entries": [{"arabic": r["arabic"], "english": r["english"]} for r in res],
        "notes": [r["note"] for r in res if r.get("note")],
        "dataset_size_words": 56,
    }
    if trace["rule"] in ("R1", "R2"):
        facts["must_mention"] = [res[0]["arabic"] if trace["language"] == "ar" else res[0]["english"]]
    elif trace["rule"] == "R3":
        facts["must_mention"] = [r["arabic"] if trace["language"] == "ar" else r["english"] for r in res]
        facts["must_say"] = "these are related entries, not the same word"
    else:
        facts["must_mention"] = []
        facts["must_say"] = "no verified sign was found in the dataset; suggest trying another word"
    return facts


def validate(text, trace, engine):
    """Return (ok, reason). The reply must agree with the trace."""
    if not text or len(text) > 400:
        return False, "empty or too long"
    if re.search(r"https?://|www\.", text):
        return False, "contains a link"
    facts = facts_from_trace(trace)
    norm_text = normalize(text)
    for label in facts["must_mention"]:
        if normalize(label) not in norm_text:
            return False, f'missing label "{label}"'
    # No other dataset label may appear (only labels of 4+ characters are checked,
    # so short everyday words like "now" do not cause false alarms).
    allowed = {r["id"] for r in trace.get("results") or []}
    for sid, e in engine.signs.items():
        if sid in allowed:
            continue
        for lab in (e["arabic"], e["english"]):
            n = normalize(lab)
            if len(n) >= 4 and re.search(rf"(?<!\w){re.escape(n)}(?!\w)", norm_text):
                return False, f'mentions another entry "{lab}"'
    if trace["rule"] == "R4" and re.search(r"(here is the sign|دي الإشارة|دي الاشاره)", text, re.I):
        return False, "claims a sign was found"
    if trace["rule"] == "R3" and not re.search(r"(not|مش|ليست|مختلف|different|related|قريب)", text, re.I):
        return False, "does not say the entry is only related"
    return True, "passed"


def phrase(trace, template_text, engine):
    """Return (reply_text, model_info) and never raise."""
    info = {"model": MODEL_ID, "prompt_version": PROMPT_VERSION, "used": False}
    if trace["rule"] not in PHRASED_RULES:
        info["status"] = "not used for this result type (fixed safety/scope text)"
        return template_text, info
    if not model_enabled():
        info["status"] = "off (no HF_TOKEN set)"
        return template_text, info

    body = {
        "model": MODEL_ID,
        "temperature": 0,
        "max_tokens": 120,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "FACTS:\n" + json.dumps(facts_from_trace(trace), ensure_ascii=False)
             + "\n\nDraft reply to rewrite:\n" + template_text},
        ],
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        info.update(status=f"error HTTP {e.code} - template used", ms=round((time.perf_counter() - t0) * 1000))
        return template_text, info
    except Exception as e:  # timeout, network, bad JSON
        info.update(status=f"error ({type(e).__name__}) - template used", ms=round((time.perf_counter() - t0) * 1000))
        return template_text, info

    info["ms"] = round((time.perf_counter() - t0) * 1000)
    info["model_text"] = text
    ok, why = validate(text, trace, engine)
    info["validator"] = why
    if not ok:
        info["status"] = "model reply rejected by validator - template used"
        return template_text, info
    info.update(used=True, status="model reply passed the validator")
    return text, info
