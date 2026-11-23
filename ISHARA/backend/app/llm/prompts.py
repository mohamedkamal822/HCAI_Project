import json


def grounded_reply_prompt(rule: str, language: str, results: list[dict], style: str, previous_reply: str = "", query: str = "") -> dict:
    labels = [result.get("arabic") if language == "ar" else result.get("english") for result in results]
    avoid_previous = f"Do not repeat or closely paraphrase this recent reply: {previous_reply}." if previous_reply else ""
    facts = {
        "rule": rule,
        "language": "Egyptian Arabic" if language == "ar" else "English",
        "verified_labels": labels,
        "searched_term": query,
        "result_type": {
            "R1": "exact catalog label match",
            "R2": "team-reviewed alternative word",
            "R3": "similar spelling only; not the same word",
            "R4": "no verified catalog match",
        }.get(rule, "verified catalog result"),
    }
    return {
        "systemInstruction": {
            "parts": [{"text": (
                "You write one helpful, concise reply for Ishara, an Egyptian Sign Language learning assistant. "
                "Return only JSON matching the schema. Use only the supplied facts; never invent signs, meanings, examples, links, or movements. "
                "For R1 and R2, include the exact verified label and invite the learner to watch or practise with its video. "
                "For R3, clearly say the suggested entries are related by spelling and are not the user's word. "
                "For R4, clearly say that no verified match was found for the supplied searched term and invite the learner to try another word or browse the catalog. "
                "Do not claim a suggested sign answers an unmatched query. Do not mention the model. "
                f"Use at most two short sentences in the requested language. Tone: {style}. {avoid_previous}"
            )}]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": "Verified facts: " + json.dumps(facts, ensure_ascii=False)}],
        }],
    }
