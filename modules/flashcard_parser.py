import json
import re


class FlashcardParseError(Exception):
    """Raised when Gemini does not return usable flashcard JSON."""


def parse_flashcard_json(raw_response):
    payload = _extract_json_payload(raw_response)

    try:
        data = json.loads(payload)

    except json.JSONDecodeError as exc:
        raise FlashcardParseError(
            "Gemini returned invalid flashcard JSON. Please generate the cards again."
        ) from exc

    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict):
        cards = data.get("flashcards") or data.get("cards")
    else:
        cards = None

    if not isinstance(cards, list) or not cards:
        raise FlashcardParseError(
            "Gemini did not return any flashcards. Please try again."
        )

    return [
        _normalize_card(card, index)
        for index, card in enumerate(cards, start=1)
    ]


def _extract_json_payload(raw_response):
    if not raw_response or not raw_response.strip():
        raise FlashcardParseError(
            "Gemini returned an empty flashcard response. Please try again."
        )

    text = raw_response.strip()
    fenced_match = re.search(
        r"```(?:json)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if fenced_match:
        return fenced_match.group(1).strip()

    object_start = text.find("{")
    object_end = text.rfind("}")
    array_start = text.find("[")
    array_end = text.rfind("]")

    if object_start != -1 and object_end != -1:
        return text[object_start:object_end + 1]

    if array_start != -1 and array_end != -1:
        return text[array_start:array_end + 1]

    return text


def _normalize_card(card, index):
    if not isinstance(card, dict):
        raise FlashcardParseError(
            f"Flashcard {index} is not in the expected format."
        )

    question = _get_value(card, ["question", "Question"])
    answer = _get_value(card, ["answer", "Answer"])
    difficulty = _get_value(card, ["difficulty", "Difficulty"]) or "Medium"
    hint = _get_value(card, ["hint", "Hint", "short_hint", "Short Hint"]) or ""
    category = _get_value(card, ["category", "Category"]) or "Concept"

    if not str(question).strip():
        raise FlashcardParseError(
            f"Flashcard {index} is missing a question."
        )

    if not str(answer).strip():
        raise FlashcardParseError(
            f"Flashcard {index} is missing an answer."
        )

    return {
        "question": str(question).strip(),
        "answer": str(answer).strip(),
        "difficulty": str(difficulty).strip(),
        "hint": str(hint).strip(),
        "category": str(category).strip(),
    }


def _get_value(source, keys):
    for key in keys:
        if key in source:
            return source[key]

    return ""
