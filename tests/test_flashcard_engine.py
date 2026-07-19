from modules.flashcard_engine import calculate_flashcard_progress, format_study_time


def test_calculate_flashcard_progress():
    cards = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"},
        {"question": "Q3", "answer": "A3"},
    ]
    statuses = {
        0: "known",
        1: "revision",
    }

    result = calculate_flashcard_progress(
        cards,
        statuses,
        90,
    )

    assert result["known_cards"] == 1
    assert result["revision_cards"] == 1
    assert result["remaining_cards"] == 1
    assert result["completion"] == 66.67
    assert result["weak_cards"] == [cards[1]]


def test_format_study_time():
    assert format_study_time(30) == "30 sec"
    assert format_study_time(130) == "2 min 10 sec"
