"""
CoMind decision engine.

Every request goes through the same steps and writes a decision trace:
  1. Normalize the input.
  2. Privacy and safety checks (R7).
  3. Exact lookup on labels (R1) and team-reviewed aliases (R2).
  4. Lookup phrases like "how do I sign X" -> X.
  5. Greeting / help / quiz requests (R0), out-of-scope (R5).
  6. Related search with a threshold (R3), or no verified match (R4).

The "Why this result?" panel is built ONLY from the trace.
The language model never chooses a video and never changes the rule.
"""

import difflib
import json
import re
import time
import unicodedata
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

ENGINE_VERSION = "engine-1.0 (2026-11-21)"
THRESHOLD = 0.70          # T, tuned in the evaluation; always shown in the panel
MAX_RELATED = 3
SIMILARITY_METHOD = "character similarity (difflib ratio)"

RULES = {
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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_index(signs_path=BACKEND_DIR / "signs.json", aliases_path=BACKEND_DIR / "aliases.json"):
    with open(signs_path, encoding="utf-8") as f:
        signs = json.load(f)
    extra = {"aliases": {}, "confusables": {}, "entry_notes": {}}
    if Path(aliases_path).exists():
        with open(aliases_path, encoding="utf-8") as f:
            extra.update({k: v for k, v in json.load(f).items() if not k.startswith("_")})
    for sid, entry in signs.items():
        merged = list(entry.get("aliases", [])) + list(extra["aliases"].get(sid, []))
        entry["aliases"] = list(dict.fromkeys(merged))
        entry["note"] = extra["entry_notes"].get(sid)
    return signs, extra["confusables"]


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

ARABIC_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
ARABIC_CHARS = re.compile(r"[؀-ۿ]")
PUNCT = re.compile(r"[^\w\s؀-ۿ]|[_؟،؛]")


def has_arabic(text):
    return bool(ARABIC_CHARS.search(text))


def normalize(text, steps=None):
    """Return the normalized text. If `steps` is a list, record each change."""
    def log(name, before, after):
        if steps is not None and before != after:
            steps.append({"step": name, "before": before, "after": after})

    t = text
    s = unicodedata.normalize("NFKC", t)
    log("unicode form", t, s); t = s

    s = ARABIC_DIACRITICS.sub("", t).replace("ـ", "")
    log("removed Arabic diacritics / tatweel", t, s); t = s

    s = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    log("unified alef and yaa forms (أ إ آ → ا, ى → ي)", t, s); t = s

    # Latin accents (fiancée -> fiancee). Arabic is not affected.
    s = "".join(c for c in unicodedata.normalize("NFKD", t)
                if not (unicodedata.combining(c) and not ARABIC_CHARS.match(c)))
    s = unicodedata.normalize("NFKC", s)
    log("removed Latin accents", t, s); t = s

    s = PUNCT.sub(" ", t)
    log("removed punctuation", t, s); t = s

    s = " ".join(t.casefold().split())
    log("lowercase and trimmed spaces", t, s); t = s
    return t
    # Note: ة and ه are NOT unified on purpose. بكرة (tomorrow) and
    # بكره (I hate) would collapse into one word. ة/ه spellings that mean
    # the same thing are listed as aliases instead.


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

LOOKUP_PATTERNS = [
    r"^(?:how (?:do|can|would) (?:i|you|we) (?:say|sign|show) )(.+?)(?: in (?:egyptian )?sign(?: language)?| in esl)?$",
    r"^(?:how to (?:say|sign) )(.+?)(?: in (?:egyptian )?sign(?: language)?| in esl)?$",
    r"^(?:what(?:'s| is) the sign for |sign for |the sign for |show me the sign for |show me |teach me )(.+)$",
    r"^(?:ازاي|كيف|ازاى) (?:اقول|اعمل|نقول|تقول|اشاور) (.+?)(?: بالاشاره| بالاشارة| بلغه الاشاره| بلغة الاشارة| بالاشارات)?$",
    r"^(?:اشاره|اشارة|الاشاره|الاشارة|علامه|علامة) (?:كلمه |كلمة )?(.+)$",
    r"^(?:عايز اتعلم|عاوز اتعلم|علمني|وريني) (?:اشاره |اشارة |كلمه |كلمة )?(.+)$",
]

GREETING = {"hi", "hello", "hey", "مرحبا", "اهلا", "اهلا بيك", "السلام عليكم", "سلام", "hii", "ازيك يا ishara"}
HELP = {"help", "مساعده", "مساعدة", "ساعدني", "what can you do", "who are you", "انت مين", "بتعمل ايه",
        "what is this", "ايه ده", "start", "ابدا"}
QUIZ = {"quiz", "test me", "start quiz", "practice", "اختبار", "امتحان", "اختبرني", "امتحني", "كويز", "تدريب"}

EMERGENCY = re.compile(
    r"(suicide|kill myself|end my life|hurt myself|emergency|انتحار|اقتل نفسي|انهي حياتي|عايز اموت|عاوز اموت|"
    r"اموت نفسي|طوارئ|اسعاف|حد بيموت|in danger)")
INTERPRET = re.compile(
    r"(interpret|interpreter|translate (?:for|a|the|this|my) (?:conversation|meeting|doctor|hospital|court|call)|"
    r"مترجم|ترجم(?:لي)? (?:محادثه|محادثة|كلام|مكالمه|مكالمة)|"
    r"(?:hospital|court|police|lawyer|surgery|مستشفي|المستشفي|محكمه|المحكمه|محكمة|قسم|محامي|عمليه) .*(?:sign|اشاره|اشارة|اصم|deaf)|"
    r"(?:sign|اشاره|اشارة|اصم|deaf).* (?:hospital|court|police|lawyer|surgery|مستشفي|المستشفي|محكمه|محكمة|المحكمه|محامي))")
ABUSE = re.compile(
    r"((?:insult|mock|offend|bully|curse at|swear at|make fun of|humiliate) (?:him|her|them|someone|somebody|my|a |the |deaf|people)|"
    r"bad words|swear words|curse words|rude signs?|offensive signs?|"
    r"(?:اشتم|اهين|اتريق علي|اضايق) (?:حد|زميلي|زميلتي|صاحبي|واحد|الاصم|الصم|ه|ها)|شتايم|شتيمه|شتيمة|الفاظ وحشه|كلام وحش)")
PHONE = re.compile(r"(?:\+?\d[\d\s-]{7,}\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
OUT_OF_SCOPE_HINTS = re.compile(
    r"(weather|news|joke|recipe|homework|code|python|football|match|price|طقس|الجو|اخبار|نكته|نكتة|وصفه|واجب|كوره|ماتش|سعر)")


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class Engine:
    def __init__(self, signs=None, confusables=None, threshold=THRESHOLD):
        if signs is None:
            signs, confusables = load_index()
        self.signs = signs
        self.threshold = threshold
        self.confusables = {normalize(k): v for k, v in (confusables or {}).items()}
        # lookup tables: normalized text -> (entry id, field, original value)
        self.label_lookup, self.alias_lookup, self.searchable = {}, {}, []
        for sid, e in signs.items():
            for field in ("arabic", "english", "franco"):
                n = normalize(e[field])
                self.label_lookup.setdefault(n, (sid, field, e[field]))
                self.searchable.append((sid, field, e[field], n))
            for a in e["aliases"]:
                n = normalize(a)
                if n not in self.label_lookup:
                    self.alias_lookup.setdefault(n, (sid, "alias", a))
                self.searchable.append((sid, "alias", a, n))

    # -- helpers -----------------------------------------------------------
    def entry_public(self, sid, lang="en"):
        e = self.signs[sid]
        note = e.get("note")
        if isinstance(note, dict):
            note = note.get(lang) or note.get("en")
        return {"id": sid, "arabic": e["arabic"], "english": e["english"],
                "franco": e["franco"], "video": e["video"], "note": note}

    def exact(self, norm):
        if norm in self.label_lookup:
            sid, field, value = self.label_lookup[norm]
            return "R1", sid, field, value
        if norm in self.alias_lookup:
            sid, field, value = self.alias_lookup[norm]
            return "R2", sid, field, value
        return None

    def score_all(self, norm):
        """Best similarity score per entry, sorted high to low."""
        best = {}
        for sid, field, value, n in self.searchable:
            sc = difflib.SequenceMatcher(None, norm, n).ratio()
            if sc > best.get(sid, (0,))[0]:
                best[sid] = (round(sc, 3), field, value)
        ranked = sorted(best.items(), key=lambda kv: kv[1][0], reverse=True)
        return [{"id": sid, "score": sc, "matched_field": f, "matched_text": v}
                for sid, (sc, f, v) in ranked]

    @staticmethod
    def extract_target(norm):
        for p in LOOKUP_PATTERNS:
            m = re.match(p, norm)
            if m:
                return m.group(1).strip(), p
        return None, None

    # -- main entry point ----------------------------------------------------
    def decide(self, message, exact_only=False, exclude=None, reply_lang=None):
        t0 = time.perf_counter()
        exclude = set(exclude or [])
        steps = []
        raw = message
        input_lang = "ar" if has_arabic(raw) else "en"
        lang = reply_lang if reply_lang in ("ar", "en") else input_lang

        trace = {
            "trace_id": uuid.uuid4().hex[:12],
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "engine_version": ENGINE_VERSION,
            "input": raw,
            "language": lang,
            "input_language": input_lang,
            "settings": {"exact_matches_only": bool(exact_only)},
            "threshold": self.threshold,
            "similarity_method": SIMILARITY_METHOD,
            "dataset": f"Egyptian Sign Language Recognition (Kaggle), {len(self.signs)} words indexed",
            "checks": [],
            "candidates": [],
            "results": [],
        }

        def check(name, outcome, detail=""):
            trace["checks"].append({"check": name, "outcome": outcome, "detail": detail})

        # 1. Privacy: mask personal data before anything else.
        masked = EMAIL.sub("[email removed]", PHONE.sub("[number removed]", raw))
        if masked != raw:
            trace["input"] = masked
            check("Personal data filter", "found", "A phone number or email was removed before processing.")
            return self._finish(trace, "R7", t0, safety="privacy")
        check("Personal data filter", "none found")

        norm = normalize(raw, steps)
        trace["normalized"] = norm
        trace["normalization_steps"] = steps

        if not norm:
            check("Input check", "empty after normalization")
            return self._finish(trace, "R5", t0, reason="empty")

        # 2. Exact lookup on the whole input first (dataset words are always allowed).
        hit = self.exact(norm)
        check("Exact lookup on full input", "match" if hit else "no match")
        if hit and hit[1] not in exclude:
            return self._exact_result(trace, hit, t0)

        # 3. Safety checks on full sentences.
        if EMERGENCY.search(norm):
            check("Safety: emergency or self-harm", "detected")
            return self._finish(trace, "R7", t0, safety="emergency")
        if INTERPRET.search(norm):
            check("Safety: high-stakes interpretation request", "detected")
            return self._finish(trace, "R7", t0, safety="interpretation")
        if ABUSE.search(norm):
            check("Safety: request to insult or hurt someone", "detected")
            return self._finish(trace, "R7", t0, safety="abuse")
        check("Safety checks", "passed")

        # 4. "How do I sign X?" -> X
        target, pattern = self.extract_target(norm)
        if target:
            trace["extracted_word"] = target
            check("Lookup phrase", "found", f'The word to look up is "{target}".')
            hit = self.exact(target)
            check("Exact lookup on extracted word", "match" if hit else "no match")
            if hit and hit[1] not in exclude:
                return self._exact_result(trace, hit, t0)
            norm = target

        # 5. Greeting / help / quiz.
        if norm in GREETING or norm in HELP:
            check("Intent", "greeting or help")
            return self._finish(trace, "R0", t0, intent="help")
        if norm in QUIZ:
            check("Intent", "quiz")
            return self._finish(trace, "R0", t0, intent="quiz")

        # 6. Confusable words (look alike, different meaning) -> related, never exact.
        if norm in self.confusables and not exact_only:
            c = self.confusables[norm]
            cnote = c.get(lang) or c.get("en")
            check("Confusable word list", "match", cnote)
            ce = self.signs[c["entry"]]
            trace["candidates"] = [{"id": c["entry"], "label": f'{ce["english"]} · {ce["arabic"]}', "score": None, "decision": "shown as related",
                                    "reason": "Team-written confusable note"}]
            trace["results"] = [{**self.entry_public(c["entry"], lang), "score": None,
                                 "reason": cnote}]
            return self._finish(trace, "R3", t0, confusable=True)

        # 7. Out of scope: long sentences or clearly unrelated topics.
        words = norm.split()
        if OUT_OF_SCOPE_HINTS.search(norm) or len(words) > 4:
            check("Scope check", "out of scope",
                  "Topic is not a sign lookup." if OUT_OF_SCOPE_HINTS.search(norm)
                  else f"{len(words)} words: CoMind looks up single words or short phrases.")
            return self._finish(trace, "R5", t0, reason="scope")
        check("Scope check", "in scope", f"{len(words)} word(s)")

        # 8. Related search.
        ranked = [c for c in self.score_all(norm) if c["id"] not in exclude]
        top = ranked[:5]
        for c in top:
            e = self.signs[c["id"]]
            if exact_only:
                c["decision"], c["reason"] = "not shown", "Exact matches only is on"
            elif c["score"] >= self.threshold:
                c["decision"], c["reason"] = "shown as related", f"score {c['score']} ≥ T {self.threshold}"
            else:
                c["decision"], c["reason"] = "rejected", f"score {c['score']} < T {self.threshold}"
            c["label"] = f'{e["english"]} · {e["arabic"]}'
        trace["candidates"] = top

        shown = [c for c in top if c["decision"] == "shown as related"][:MAX_RELATED]
        if shown:
            for c in shown:
                e = self.signs[c["id"]]
                if lang == "ar":
                    reason = (f'الكلمة دي مكتوبة شبه «{c["matched_text"]}» بنسبة {round(c["score"]*100)}% '
                              f'(بنعرض بس الكلمات اللي تشابهها {round(self.threshold*100)}% أو أكتر). '
                              f'معناها في الداتا «{e["arabic"]}»، ومش هي الكلمة اللي انت كتبتها.')
                else:
                    reason = (f'Spelling is similar to "{c["matched_text"]}" (score {c["score"]} ≥ T {self.threshold}). '
                              f'In our dataset this sign means "{e["english"]}" ({e["arabic"]}). '
                              f"It is not the word you typed.")
                pub = self.entry_public(c["id"], lang)
                if pub.get("note"):
                    reason += " " + pub["note"]
                trace["results"].append({**pub, "score": c["score"], "reason": reason})
            return self._finish(trace, "R3", t0)

        return self._finish(trace, "R4", t0)

    # -- result builders -----------------------------------------------------
    def _exact_result(self, trace, hit, t0):
        rule, sid, field, value = hit
        trace["matched_field"] = field
        trace["matched_text"] = value
        trace["results"] = [{**self.entry_public(sid, trace["language"]), "score": 1.0,
                             "reason": self._exact_reason(rule, field, value, sid, trace["language"])}]
        return self._finish(trace, rule, t0)

    def _exact_reason(self, rule, field, value, sid, lang):
        e = self.signs[sid]
        if lang == "ar":
            if rule == "R1":
                return f"الكلمة اللي كتبتها هي نفس الكلمة «{value}» اللي في الداتا بالظبط."
            return f"«{value}» طريقة تانية بنقول بيها «{e['arabic']}»، وفريقنا راجعها."
        if rule == "R1":
            return f'Your word matched the dataset {field} label "{value}".'
        return f'Your word matched "{value}", a team-reviewed alternative word for this entry.'

    def _finish(self, trace, rule, t0, **extra):
        trace["rule"] = rule
        trace["rule_name"] = RULES[rule]
        trace["badge"] = BADGES[rule]
        trace.update({k: v for k, v in extra.items() if v is not None})
        if rule == "R4" and trace["candidates"]:
            best = trace["candidates"][0]
            trace["best_candidate"] = {"id": best["id"], "label": best.get("label"), "score": best["score"]}
        trace["decision_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return trace


# ---------------------------------------------------------------------------
# Template replies (used when the model is off, fails, or fails validation)
# ---------------------------------------------------------------------------

EXAMPLES_AR = "صباح الخير، دكتور، عامل إيه، كتاب"
EXAMPLES_EN = "Good morning, Doctor, How are you, Book"


def template_reply(trace):
    r, ar = trace["rule"], trace["language"] == "ar"
    res = trace.get("results") or []
    first = res[0] if res else None

    if r in ("R1", "R2"):
        alt = "" if r == "R1" else (" (لقيناها بكلمة تانية بنفس المعنى)" if ar else " (found through an alternative word)")
        txt = (f"تمام! دي إشارة «{first['arabic']}»، وإحنا متأكدين منها من الداتا بتاعتنا{alt}."
               if ar else f'Here is the verified sign for "{first["english"]}" ({first["arabic"]}){alt}.')
        return txt   # entry notes are shown on the result card, in the reply language
    if r == "R3":
        labels = "، ".join(f"«{x['arabic']}»" for x in res) if ar else ", ".join(f'"{x["english"]}"' for x in res)
        if trace.get("confusable"):
            return (f"الكلمة دي مش عندنا. فيه كلمة شكلها شبهها هي {labels}، بس معناها مختلف، فخلي بالك."
                    if ar else f"I don't have a verified sign for that word. The closest-looking entry is {labels}, but it means something different.")
        return (f"ملقيتش الكلمة دي بالظبط. لقيت كلمة مكتوبة شبهها: {labels}، بس دي كلمة تانية، مش نفس كلمتك."
                if ar else f"I couldn't find that exact word. These entries look similar, but they are not the same word: {labels}.")
    if r == "R4":
        q = trace.get("extracted_word") or trace.get("normalized") or trace["input"]
        if trace["settings"]["exact_matches_only"]:
            extra_ar, extra_en = " (إنت قافل «الكلمات القريبة» من الإعدادات.)", " (Related words are switched off in settings.)"
        else:
            extra_ar = extra_en = ""
        return (f"للأسف معنديش إشارة متأكد منها لكلمة «{q}»، لأن الداتا بتاعتنا فيها 56 كلمة بس. ده مش معناه إن الكلمة ملهاش إشارة في لغة الإشارة المصرية. جرب كلمة تانية زي: {EXAMPLES_AR}، أو اسأل مدرس لغة إشارة.{extra_ar}"
                if ar else f'I couldn\'t find a verified sign for "{q}" in our dataset (56 words). This doesn\'t mean the sign doesn\'t exist in Egyptian Sign Language. Try another word such as {EXAMPLES_EN}, or ask a qualified sign language teacher.{extra_en}')
    if r == "R5":
        return ("أنا بساعدك تتعلم إشارات الكلمات بس في لغة الإشارة المصرية. اكتب كلمة واحدة أو كلمتين، أو جرب الاختبار."
                if ar else "I can only help you learn signs for single words or short phrases in Egyptian Sign Language. Type one word, or open the quiz.")
    if r == "R0":
        if trace.get("intent") == "quiz":
            return ("يلا بينا! اضغط «افتح الاختبار» واتمرن على الإشارات بالفيديو."
                    if ar else "Great! Press “Open the quiz” to practise reading signs from videos.")
        return ("أهلاً بيك! أنا «إشارة»، مساعد ذكاء اصطناعي بيوريك فيديوهات إشارات متأكدين منها لـ56 كلمة. اكتب أي كلمة بالعربي أو الإنجليزي. مقدرش أترجم محادثة ولا أألف إشارة من عندي."
                if ar else "Hi! I'm an AI assistant that shows verified sign videos from a dataset of 56 words. Type a word in Arabic or English. I can't interpret conversations or make up signs.")
    if r == "R7":
        kind = trace.get("safety")
        if kind == "emergency":
            return ("لو إنت أو حد تاني في خطر، كلم الإسعاف ١٢٣ أو الشرطة ١٢٢ دلوقتي، أو اتكلم مع حد بتثق فيه. أنا أداة تعليمية ومش بقدر أساعد في الطوارئ."
                    if ar else "If you or someone else is in danger, call 123 (ambulance) or 122 (police) in Egypt now, or talk to someone you trust. I'm a learning tool and can't help in an emergency.")
        if kind == "interpretation":
            return ("في المواقف المهمة زي الدكتور أو المحكمة أو أي مشوار رسمي، لازم تستعين بمترجم لغة إشارة مصرية متخصص، أو تكلم جمعية للصم قريبة منك. أنا بعلّم كلمات لوحدها بس، ومقدرش أترجم كلام بين الناس."
                    if ar else "For medical, legal or official conversations, please use a qualified Egyptian Sign Language interpreter or your local Deaf association. I only show single-word signs and can't interpret a conversation.")
        if kind == "abuse":
            return ("معلش، مش هقدر أساعد في إشارات الهدف منها إننا نهين أو نضايق حد. لو عايز تعرف معنى كلمة معينة، اكتبها لوحدها."
                    if ar else "I can't help with signs meant to insult or hurt someone. You can still look up a single word to learn what it means.")
        if kind == "privacy":
            return ("شلت معلومات شخصية (رقم أو إيميل) من رسالتك. من فضلك متكتبش بيانات شخصية هنا. اكتب الكلمة اللي عايز تتعلمها بس."
                    if ar else "I removed personal information (a number or email) from your message. Please don't share personal details here. Just type the word you want to learn.")
    if r == "R6":
        return ("معلش، حصلت مشكلة عندنا. جرب تاني، أو عدّل الكلمة."
                if ar else "Something went wrong on our side. Please try again, or edit your word.")
    return "…"
