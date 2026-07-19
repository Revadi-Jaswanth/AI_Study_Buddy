from modules.gemini_config import generate_content
from modules.prompts import quiz_json_prompt
from modules.quiz_parser import parse_quiz_json


def generate_interactive_quiz(topic, difficulty, question_count):

    raw_response = generate_content(
        quiz_json_prompt(topic, difficulty, question_count)
    )

    questions = parse_quiz_json(
        raw_response,
        question_count
    )

    return {
        "topic": topic,
        "difficulty": difficulty,
        "question_count": question_count,
        "questions": questions,
        "raw_response": raw_response,
    }


def calculate_quiz_result(questions, answers, time_taken_seconds):
    total_questions = len(questions)
    correct_count = 0
    review_items = []

    for index, question in enumerate(questions):
        selected_answer = answers.get(index)
        is_correct = selected_answer == question["correct_answer"]

        if is_correct:
            correct_count += 1

        review_items.append(
            {
                "question_number": index + 1,
                "question": question["question"],
                "options": question["options"],
                "student_answer": selected_answer,
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"],
                "is_correct": is_correct,
            }
        )

    percentage = round(
        (correct_count / total_questions) * 100,
        2
    ) if total_questions else 0

    return {
        "score": correct_count,
        "total_questions": total_questions,
        "percentage": percentage,
        "correct_answers": correct_count,
        "wrong_answers": total_questions - correct_count,
        "time_taken_seconds": time_taken_seconds,
        "review_items": review_items,
    }


def format_time_taken(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes:
        return f"{minutes} min {remaining_seconds} sec"

    return f"{remaining_seconds} sec"


def build_quiz_result_markdown(topic, difficulty, result):
    lines = [
        f"# Quiz Result: {topic}",
        "",
        f"Difficulty: {difficulty}",
        f"Score: {result['score']} / {result['total_questions']}",
        f"Percentage: {result['percentage']}%",
        f"Correct Answers: {result['correct_answers']}",
        f"Wrong Answers: {result['wrong_answers']}",
        f"Time Taken: {format_time_taken(result['time_taken_seconds'])}",
        "",
        "## Review",
    ]

    for item in result["review_items"]:
        student_answer = item["student_answer"] or "Not answered"
        lines.extend(
            [
                "",
                f"### Question {item['question_number']}",
                item["question"],
                f"- Student Answer: {student_answer}",
                f"- Correct Answer: {item['correct_answer']}",
                f"- Explanation: {item['explanation']}",
            ]
        )

    return "\n".join(lines)
