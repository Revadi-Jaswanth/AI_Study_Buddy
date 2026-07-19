import json
import re


class QuizParseError(Exception):
    """Raised when Gemini does not return a usable quiz payload."""


def parse_quiz_json(raw_response, expected_count):
    payload = _extract_json_payload(raw_response)

    try:
        data = json.loads(payload)

    except json.JSONDecodeError as exc:
        raise QuizParseError(
            "Gemini returned invalid quiz JSON. Please generate the quiz again."
        ) from exc

    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict):
        questions = data.get("questions")
    else:
        questions = None

    if not isinstance(questions, list) or not questions:
        raise QuizParseError(
            "Gemini did not return any quiz questions. Please try again."
        )

    if len(questions) < expected_count:
        raise QuizParseError(
            "Gemini returned fewer questions than requested. Please try again."
        )

    return [
        _normalize_question(question, index)
        for index, question in enumerate(questions[:expected_count], start=1)
    ]


def _extract_json_payload(raw_response):
    if not raw_response or not raw_response.strip():
        raise QuizParseError(
            "Gemini returned an empty quiz response. Please try again."
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


def _normalize_question(question, index):
    if not isinstance(question, dict):
        raise QuizParseError(
            f"Question {index} is not in the expected format."
        )

    prompt = _get_value(question, ["question", "Question"])
    correct_answer = _normalize_answer(
        _get_value(question, ["correct_answer", "Correct Answer", "correctAnswer", "answer"])
    )
    explanation = _get_value(question, ["explanation", "Explanation"])
    difficulty = _get_value(question, ["difficulty", "Difficulty"])
    topic = _get_value(question, ["topic", "Topic"])
    options = _normalize_options(question)

    if not prompt:
        raise QuizParseError(
            f"Question {index} is missing the question text."
        )

    if correct_answer not in options:
        raise QuizParseError(
            f"Question {index} has an invalid correct answer."
        )

    return {
        "question": str(prompt).strip(),
        "options": options,
        "correct_answer": correct_answer,
        "explanation": str(explanation).strip() if explanation else "No explanation provided.",
        "difficulty": str(difficulty).strip() if difficulty else "",
        "topic": str(topic).strip() if topic else "",
    }


def _normalize_options(question):
    options = question.get("options")

    if isinstance(options, dict):
        normalized = {
            letter: str(options.get(letter, options.get(letter.lower(), ""))).strip()
            for letter in ["A", "B", "C", "D"]
        }
    else:
        normalized = {
            "A": str(_get_value(question, ["option_a", "Option A", "A"])).strip(),
            "B": str(_get_value(question, ["option_b", "Option B", "B"])).strip(),
            "C": str(_get_value(question, ["option_c", "Option C", "C"])).strip(),
            "D": str(_get_value(question, ["option_d", "Option D", "D"])).strip(),
        }

    if any(not value for value in normalized.values()):
        raise QuizParseError(
            "One or more quiz options are missing."
        )

    return normalized


def _get_value(source, keys):
    for key in keys:
        if key in source:
            return source[key]

    return ""


def _normalize_answer(value):
    answer = str(value).strip().upper()

    if answer.startswith("OPTION "):
        answer = answer.replace("OPTION ", "", 1).strip()

    if answer and answer[0] in ["A", "B", "C", "D"]:
        return answer[0]

    return answer
