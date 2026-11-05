def acknowledgement_prompt(result_type: str, arabic: str, english: str, style: str, previous_reply: str = "") -> dict:
    avoid_previous = f"Do not repeat or closely paraphrase this recent reply: {previous_reply}." if previous_reply else ""
    return {
        "systemInstruction": {
            "parts": [{"text": (
                "Write one short, useful Egyptian Arabic reply for a sign-language learning app. "
                "Return only JSON matching the schema. Mention the exact Arabic sign term provided. "
                "Stay tied to that result: say it was found in the sign library and tell the learner to view or practice with its video. "
                "Do not explain the sign's meaning or movement, invent facts, offer unrelated greetings, or mention the AI/model. "
                "Use four to fourteen Arabic words and no English or URLs."
            )}]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": (
                f"Verified match type: {result_type}. Exact Arabic term: {arabic}. "
                f"Verified English gloss for context only: {english}. Tone: {style}. {avoid_previous}"
            )}],
        }],
    }
