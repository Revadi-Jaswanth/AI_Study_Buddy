from modules.flashcard_parser import parse_flashcard_json
from modules.gemini_config import generate_content
from modules.prompts import flashcards_json_prompt


def generate_interactive_flashcards(topic, card_count=10):

    raw_response = generate_content(
        flashcards_json_prompt(topic, card_count)
    )
    flashcards = parse_flashcard_json(
        raw_response
    )

    return {
        "topic": topic,
        "card_count": len(flashcards),
        "flashcards": flashcards,
        "raw_response": raw_response,
    }


def calculate_flashcard_progress(cards, statuses, study_time_seconds):
    total_cards = len(cards)
    known_cards = sum(
        1
        for status in statuses.values()
        if status == "known"
    )
    revision_cards = sum(
        1
        for status in statuses.values()
        if status == "revision"
    )
    studied_cards = known_cards + revision_cards
    remaining_cards = max(
        total_cards - studied_cards,
        0
    )
    completion = round(
        (studied_cards / total_cards) * 100,
        2
    ) if total_cards else 0

    return {
        "total_cards": total_cards,
        "cards_studied": studied_cards,
        "known_cards": known_cards,
        "revision_cards": revision_cards,
        "remaining_cards": remaining_cards,
        "completion": completion,
        "study_time_seconds": study_time_seconds,
        "weak_cards": [
            cards[index]
            for index, status in statuses.items()
            if status == "revision" and index < total_cards
        ],
    }


def build_flashcards_markdown(topic, flashcards):
    lines = [
        f"# Flashcards: {topic}",
        "",
    ]

    for index, card in enumerate(flashcards, start=1):
        lines.extend(
            [
                f"## Card {index}",
                f"Difficulty: {card['difficulty']}",
                f"Category: {card.get('category', 'Concept')}",
            ]
        )

        if card.get("hint"):
            lines.append(f"Hint: {card['hint']}")

        lines.extend(
            [
                f"Question: {card['question']}",
                f"Answer: {card['answer']}",
                "",
            ]
        )

    return "\n".join(lines)


def format_study_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes:
        return f"{minutes} min {remaining_seconds} sec"

    return f"{remaining_seconds} sec"
