import csv
import io


def seconds_to_label(seconds):
    seconds = int(seconds or 0)
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes:
        return f"{minutes} min {remaining_seconds} sec"

    return f"{remaining_seconds} sec"


def analytics_to_markdown(data):
    summary = data["summary"]
    performance = data["performance"]

    return f"""
# Analytics Dashboard

## Dashboard Cards
- Total AI Requests: {summary['total_ai_requests']}
- Total Topics Explained: {summary['total_topics_explained']}
- Total Notes Summarized: {summary['total_notes_summarized']}
- Total Quizzes Taken: {summary['total_quizzes_taken']}
- Total Flashcard Sessions: {summary['total_flashcard_sessions']}
- Total Study Plans Created: {summary['total_study_plans_created']}
- Total Doubts Solved: {summary['total_doubts_solved']}
- Total PDFs Exported: {summary['total_pdfs_exported']}

## Learning Performance
- Highest Quiz Score: {performance['highest_quiz_score']}%
- Average Quiz Score: {performance['average_quiz_score']}%
- Lowest Quiz Score: {performance['lowest_quiz_score']}%
- Overall Accuracy: {performance['overall_accuracy']}%
- Average Study Session Duration: {seconds_to_label(performance['average_study_session_duration'])}
- Most Studied Topic: {performance['most_studied_topic']}
- Least Studied Topic: {performance['least_studied_topic']}
- Weekly Learning Streak: {performance['weekly_learning_streak']} day(s)
- Most Active Day: {performance['most_active_day']}
- Average Questions Per Quiz: {performance['average_questions_per_quiz']}
- Average Flashcard Completion: {performance['average_flashcard_completion']}%
"""


def activity_to_csv(activity_rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Feature",
            "Topic",
            "Date",
            "Status",
        ]
    )

    for row in activity_rows:
        writer.writerow(
            [
                row["feature"],
                row["topic"],
                row["activity_date"],
                row["status"],
            ]
        )

    return output.getvalue().encode("utf-8")
