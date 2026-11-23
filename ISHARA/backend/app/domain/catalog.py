import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote

from ..core.config import ALIASES_PATH, RELATED_THRESHOLD


ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670]")
PUNCTUATION = re.compile(r"[^\w\s]", re.UNICODE)
ARABIC_VARIANTS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ـ": ""})


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", text).casefold())
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    normalized = normalized.translate(ARABIC_VARIANTS)
    normalized = ARABIC_DIACRITICS.sub("", normalized)
    normalized = PUNCTUATION.sub(" ", normalized)
    return " ".join(normalized.split())


class SignCatalog:
    def __init__(self, signs_path: Path, aliases_path: Path = ALIASES_PATH):
        with signs_path.open("r", encoding="utf-8") as file:
            self.signs: dict[str, dict] = json.load(file)
        with aliases_path.open("r", encoding="utf-8") as file:
            self.alias_data = json.load(file)

        reviewed_aliases = self.alias_data.get("aliases", {})
        for sign_id, sign in self.signs.items():
            existing = sign.get("aliases", [])
            additional = reviewed_aliases.get(sign_id, [])
            seen = {normalize_text(alias) for alias in existing}
            sign["aliases"] = list(existing)
            for alias in additional:
                normalized_alias = normalize_text(alias)
                if normalized_alias not in seen:
                    sign["aliases"].append(alias)
                    seen.add(normalized_alias)

        self.confusables = {
            normalize_text(term): details
            for term, details in self.alias_data.get("confusables", {}).items()
        }
        self.entry_notes = self.alias_data.get("entry_notes", {})

    def find(self, message: str) -> tuple[dict | None, str | None, str | None, str | None]:
        search_term = normalize_text(message)
        for sign in self.signs.values():
            for field in ("arabic", "english", "franco"):
                value = sign.get(field)
                if value and normalize_text(value) == search_term:
                    return sign, "R1", field, value
        for sign in self.signs.values():
            for alias in sign.get("aliases", []):
                if normalize_text(alias) == search_term:
                    return sign, "R2", "alias", alias
        return None, None, None, None

    def similarity_candidates(self, message: str, limit: int = 3) -> list[dict]:
        search_term = normalize_text(message)
        if not search_term:
            return []

        candidates = []
        for sign in self.signs.values():
            terms = [sign.get(field, "") for field in ("arabic", "english", "franco")]
            terms.extend(sign.get("aliases", []))
            scored_terms = [
                (SequenceMatcher(None, search_term, normalize_text(term)).ratio(), term)
                for term in terms
                if term and normalize_text(term)
            ]
            if not scored_terms:
                continue
            score, matched_term = max(scored_terms, key=lambda item: item[0])
            candidates.append({
                "id": sign["id"],
                "arabic": sign["arabic"],
                "english": sign["english"],
                "score": round(score, 3),
                "matched_term": matched_term,
                "relation_note": self._relation_note(sign, message),
                "video_url": self.video_url(sign),
            })

        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]

    @staticmethod
    def _relation_note(sign: dict, message: str) -> str | None:
        search_term = normalize_text(message)
        relations = sign.get("relations", [])
        for relation in relations:
            if normalize_text(relation.get("term", "")) == search_term and relation.get("note"):
                return relation["note"]
        relation_notes = sign.get("relation_notes", {})
        for term, note in relation_notes.items():
            if normalize_text(term) == search_term and note:
                return note
        return None

    def confusable(self, message: str) -> dict | None:
        return self.confusables.get(normalize_text(message))

    def entry_note(self, sign_id: str) -> dict | None:
        return self.entry_notes.get(sign_id)

    def aliases_for(self, sign_id: str) -> list[str]:
        return self.signs[sign_id].get("aliases", [])

    def best_candidate(self, message: str) -> dict | None:
        candidates = self.similarity_candidates(message, limit=1)
        return candidates[0] if candidates else None

    def video_url(self, sign: dict) -> str:
        relative_path = Path(sign["video"]).relative_to("dataset")
        return f"/videos/{quote(relative_path.as_posix(), safe='/')}"

    def examples(self, limit: int = 4) -> list[str]:
        return [sign["arabic"] for sign in list(self.signs.values())[:limit]]
