from modules.quiz_engine import calculate_quiz_result, format_time_taken


def test_calculate_quiz_result_scores_answers():
    questions = [
        {
            "question": "Q1",
            "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
            "correct_answer": "A",
            "explanation": "A is correct.",
        },
        {
            "question": "Q2",
            "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
            "correct_answer": "C",
            "explanation": "C is correct.",
        },
    ]

    result = calculate_quiz_result(
        questions,
        {0: "A", 1: "B"},
        75,
    )

    assert result["score"] == 1
    assert result["percentage"] == 50.0
    assert result["wrong_answers"] == 1
    assert result["review_items"][1]["is_correct"] is False


def test_format_time_taken():
    assert format_time_taken(45) == "45 sec"
    assert format_time_taken(125) == "2 min 5 sec"
