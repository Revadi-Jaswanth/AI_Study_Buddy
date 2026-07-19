from modules.prompts import (
    flashcards_json_prompt,
    quiz_json_prompt,
    topic_explainer_prompt,
)


def test_topic_prompt_contains_required_sections():
    prompt = topic_explainer_prompt("Operating Systems", "Beginner")

    assert "# Overview" in prompt
    assert "# Interview Questions" in prompt
    assert "Personalization Context" in prompt


def test_quiz_prompt_requests_json_only():
    prompt = quiz_json_prompt("DBMS", "Medium", 5)

    assert "Return ONLY valid JSON" in prompt
    assert '"questions"' in prompt
    assert "Create exactly 5 questions" in prompt


def test_flashcard_prompt_requests_structured_cards():
    prompt = flashcards_json_prompt("Python", 10)

    assert "Return ONLY valid JSON" in prompt
    assert '"flashcards"' in prompt
    assert "Create exactly 10 flashcards" in prompt
