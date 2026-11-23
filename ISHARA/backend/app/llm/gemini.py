import json
import os
import re
from collections import deque
from secrets import choice

import httpx

from ..core.config import GEMINI_API_URL, gemini_model
from .prompts import grounded_reply_prompt

REPLY_STYLES = ("warm and encouraging", "calm and clear", "natural and direct", "supportive and professional", "concise and friendly")


class GeminiAPIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class GeminiService:
    def __init__(self):
        self._recent_phrases: deque[str] = deque(maxlen=8)

    def generate_relevant_reply(self, rule: str, language: str, results: list[dict], query: str = "") -> tuple[str | None, dict]:
        token = os.getenv("GEMINI_API_KEY")
        model = gemini_model()
        if not token:
            return None, {"used": False, "reason": "GEMINI_API_KEY is not configured"}
        if not os.getenv("GEMINI_KEY_ROTATED_AT"):
            return None, {"used": False, "reason": "GEMINI_API_KEY requires rotation confirmation"}

        for _ in range(2):
            style = choice(REPLY_STYLES)
            phrase, metadata = self._generate(token, model, rule, language, results, style, query)
            if phrase and phrase not in self._recent_phrases:
                self._recent_phrases.append(phrase)
                return phrase, metadata
        return None, {"used": False, "reason": "RepeatedOrInvalidModelResponse", "model": model}

    def list_models(self, query: str = "") -> list[str]:
        token = os.getenv("GEMINI_API_KEY")
        if not token:
            raise GeminiAPIError(503, "GEMINI_API_KEY is not configured.")
        try:
            response = httpx.get(GEMINI_API_URL, headers={"x-goog-api-key": token}, timeout=15)
            response.raise_for_status()
            models = response.json().get("models", [])
        except httpx.HTTPStatusError as error:
            raise GeminiAPIError(error.response.status_code, self._provider_detail(error.response)) from error
        except httpx.HTTPError as error:
            raise GeminiAPIError(503, "Unable to reach Google AI Studio.") from error
        model_ids = [item.get("name", "").removeprefix("models/") for item in models if item.get("name")]
        if query:
            model_ids = [item for item in model_ids if query.casefold() in item.casefold()]
        return model_ids

    def _generate(self, token: str, model: str, rule: str, language: str, results: list[dict], style: str, query: str) -> tuple[str | None, dict]:
        payload = grounded_reply_prompt(rule, language, results, style, self._recent_phrases[-1] if self._recent_phrases else "", query)
        payload["generationConfig"] = {
            "temperature": 0.85,
            "maxOutputTokens": 160,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {"phrase": {"type": "STRING"}},
                "required": ["phrase"],
                "propertyOrdering": ["phrase"],
            },
        }
        try:
            response = httpx.post(
                f"{GEMINI_API_URL}/{model}:generateContent",
                headers={"x-goog-api-key": token},
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            phrase = json.loads(text)["phrase"].strip()
            labels = [item.get("arabic" if language == "ar" else "english", "") for item in results]
            valid_language = bool(re.search(r"[\u0600-\u06ff]", phrase)) if language == "ar" else bool(re.search(r"[A-Za-z]", phrase))
            has_grounded_label = rule not in {"R1", "R2"} or any(label and label.casefold() in phrase.casefold() for label in labels)
            requires_nonmatch_clarity = rule not in {"R3", "R4"} or bool(re.search(r"مش نفس|مش الكلمة|قريبة|ملقيتش|لم أجد|لم اجد|مفيش|لا توجد|مش موجود|not the same|similar|no verified|could not find|no match", phrase, re.I))
            if len(phrase) > 300 or "\n" in phrase or not valid_language or not has_grounded_label or not requires_nonmatch_clarity or re.search(r"https?://|www\.", phrase):
                return None, {"used": False, "reason": "IrrelevantOrInvalidModelResponse", "model": model}
            return phrase, {"used": True, "model": model, "style": style, "grounded_in": labels, "rule": rule}
        except httpx.HTTPStatusError as error:
            return None, {
                "used": False,
                "reason": "HTTPStatusError",
                "http_status": error.response.status_code,
                "provider_detail": self._provider_detail(error.response),
            }
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            return None, {"used": False, "reason": type(error).__name__, "model": model}

    @staticmethod
    def _provider_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
            error = payload.get("error", payload.get("message", ""))
            if isinstance(error, dict):
                error = error.get("message", "")
            if isinstance(error, str):
                return error[:300]
        except (ValueError, TypeError):
            pass
        return "The inference provider rejected the request."
