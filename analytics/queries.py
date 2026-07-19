import streamlit as st
from database.queries import fetch_all, fetch_one


FEATURE_NAMES = [
    "Topic Explainer",
    "Notes Summarizer",
    "Quiz Generator",
    "Flashcards",
    "Study Planner",
    "Doubt Solver",
]


def get_filter_options():
    return {
        "features": [
            "All Features",
            *FEATURE_NAMES,
            "Quiz Attempts",
            "Flashcard Sessions",
            "PDF Export",
            "All Workspace Pages",
        ]
    }


@st.cache_data(ttl=10, show_spinner=False)
def get_dashboard_data(user_id, start_date=None, end_date=None, feature="All Features", topic=""):
    filters = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "feature": feature,
        "topic": topic,
    }

    return {
        "summary": _get_summary(filters),
        "performance": _get_performance(filters),
        "feature_usage": _get_feature_usage(filters),
        "weekly_activity": _get_weekly_activity(filters),
        "quiz_performance": _get_quiz_performance(filters),
        "study_time": _get_study_time(filters),
        "topic_distribution": _get_topic_distribution(filters),
        "quiz_difficulty": _get_quiz_difficulty(filters),
        "recent_activity": _get_recent_activity(filters),
    }


def _date_clause(column_name, filters, params):
    clauses = []

    if filters["start_date"]:
        clauses.append(f"DATE({column_name}) >= %s")
        params.append(filters["start_date"])

    if filters["end_date"]:
        clauses.append(f"DATE({column_name}) <= %s")
        params.append(filters["end_date"])

    return clauses


def _history_where(filters, params):
    clauses = ["user_id = %s"]
    params.append(filters["user_id"])
    clauses.extend(_date_clause("created_at", filters, params))

    if filters["feature"] in FEATURE_NAMES:
        clauses.append("feature_name = %s")
        params.append(filters["feature"])
    elif filters["feature"] != "All Features":
        clauses.append("1 = 0")

    if filters["topic"]:
        clauses.append("user_prompt LIKE %s")
        params.append(f"%{filters['topic']}%")

    return f"WHERE {' AND '.join(clauses)}" if clauses else ""


def _quiz_where(filters, params):
    clauses = ["user_id = %s"]
    params.append(filters["user_id"])
    clauses.extend(_date_clause("created_at", filters, params))

    if filters["feature"] not in ["All Features", "Quiz Attempts", "Quiz Generator"]:
        clauses.append("1 = 0")

    if filters["topic"]:
        clauses.append("topic LIKE %s")
        params.append(f"%{filters['topic']}%")

    return f"WHERE {' AND '.join(clauses)}" if clauses else ""


def _flashcard_where(filters, params):
    clauses = ["user_id = %s"]
    params.append(filters["user_id"])
    clauses.extend(_date_clause("created_at", filters, params))

    if filters["feature"] not in ["All Features", "Flashcard Sessions", "Flashcards"]:
        clauses.append("1 = 0")

    if filters["topic"]:
        clauses.append("topic LIKE %s")
        params.append(f"%{filters['topic']}%")

    return f"WHERE {' AND '.join(clauses)}" if clauses else ""


def _pdf_where(filters, params):
    clauses = ["user_id = %s"]
    params.append(filters["user_id"])
    clauses.extend(_date_clause("created_at", filters, params))

    if filters["feature"] not in ["All Features", "PDF Export"]:
        clauses.append("1 = 0")

    if filters["topic"]:
        clauses.append("topic LIKE %s")
        params.append(f"%{filters['topic']}%")

    return f"WHERE {' AND '.join(clauses)}" if clauses else ""


def _count_history_feature(feature_name, filters):
    if filters["feature"] not in ["All Features", feature_name]:
        return 0

    params = []
    where_clause = _history_where(
        {
            **filters,
            "feature": feature_name,
        },
        params
    )
    row = fetch_one(
        f"""
        SELECT COUNT(*) AS total
        FROM history
        {where_clause}
        """,
        tuple(params)
    )

    return row["total"] if row else 0


def _get_summary(filters):
    history_params = []
    history_where = _history_where(filters, history_params)
    total_ai = fetch_one(
        f"""
        SELECT COUNT(*) AS total
        FROM history
        {history_where}
        """,
        tuple(history_params)
    )

    quiz_params = []
    quiz_where = _quiz_where(filters, quiz_params)
    total_quizzes = fetch_one(
        f"SELECT COUNT(*) AS total FROM quiz_attempts {quiz_where}",
        tuple(quiz_params)
    )

    flashcard_params = []
    flashcard_where = _flashcard_where(filters, flashcard_params)
    total_flashcards = fetch_one(
        f"SELECT COUNT(*) AS total FROM flashcard_sessions {flashcard_where}",
        tuple(flashcard_params)
    )

    pdf_params = []
    pdf_where = _pdf_where(filters, pdf_params)
    total_pdfs = fetch_one(
        f"SELECT COUNT(*) AS total FROM pdf_exports {pdf_where}",
        tuple(pdf_params)
    )

    return {
        "total_ai_requests": total_ai["total"] if total_ai else 0,
        "total_topics_explained": _count_history_feature("Topic Explainer", filters),
        "total_notes_summarized": _count_history_feature("Notes Summarizer", filters),
        "total_quizzes_taken": total_quizzes["total"] if total_quizzes else 0,
        "total_flashcard_sessions": total_flashcards["total"] if total_flashcards else 0,
        "total_study_plans_created": _count_history_feature("Study Planner", filters),
        "total_doubts_solved": _count_history_feature("Doubt Solver", filters),
        "total_pdfs_exported": total_pdfs["total"] if total_pdfs else 0,
    }


def _get_performance(filters):
    quiz_params = []
    quiz_where = _quiz_where(filters, quiz_params)
    quiz_stats = fetch_one(
        f"""
        SELECT
            MAX(percentage) AS highest_score,
            AVG(percentage) AS average_score,
            MIN(percentage) AS lowest_score,
            AVG(percentage) AS overall_accuracy,
            AVG(question_count) AS average_questions
        FROM quiz_attempts
        {quiz_where}
        """,
        tuple(quiz_params)
    )

    flashcard_params = []
    flashcard_where = _flashcard_where(filters, flashcard_params)
    flashcard_stats = fetch_one(
        f"""
        SELECT
            AVG(completion) AS average_flashcard_completion,
            AVG(study_time_seconds) AS average_flashcard_time
        FROM flashcard_sessions
        {flashcard_where}
        """,
        tuple(flashcard_params)
    )

    quiz_time = fetch_one(
        f"SELECT AVG(time_taken_seconds) AS average_quiz_time FROM quiz_attempts {quiz_where}",
        tuple(quiz_params)
    )

    topic_rows = _get_topic_distribution(filters)
    most_topic = topic_rows[0]["topic"] if topic_rows else "None"
    least_topic = topic_rows[-1]["topic"] if topic_rows else "None"

    return {
        "highest_quiz_score": round(quiz_stats["highest_score"] or 0, 2) if quiz_stats else 0,
        "average_quiz_score": round(quiz_stats["average_score"] or 0, 2) if quiz_stats else 0,
        "lowest_quiz_score": round(quiz_stats["lowest_score"] or 0, 2) if quiz_stats else 0,
        "overall_accuracy": round(quiz_stats["overall_accuracy"] or 0, 2) if quiz_stats else 0,
        "average_questions_per_quiz": round(quiz_stats["average_questions"] or 0, 2) if quiz_stats else 0,
        "average_flashcard_completion": round(flashcard_stats["average_flashcard_completion"] or 0, 2)
        if flashcard_stats else 0,
        "average_study_session_duration": round(
            _average_nonzero(
                [
                    quiz_time["average_quiz_time"] if quiz_time else 0,
                    flashcard_stats["average_flashcard_time"] if flashcard_stats else 0,
                ]
            ),
            2
        ),
        "most_studied_topic": most_topic,
        "least_studied_topic": least_topic,
        "most_active_day": _get_most_active_day(filters),
        "weekly_learning_streak": _get_weekly_learning_streak(filters),
    }


def _get_feature_usage(filters):
    params = []
    where_clause = _history_where(filters, params)
    rows = fetch_all(
        f"""
        SELECT feature_name, COUNT(*) AS usage_count
        FROM history
        {where_clause}
        GROUP BY feature_name
        """,
        tuple(params)
    )
    usage_map = {
        row["feature_name"]: row["usage_count"]
        for row in rows
    }

    return [
        {
            "feature": feature,
            "usage_count": usage_map.get(feature, 0),
        }
        for feature in FEATURE_NAMES
    ]


def _get_weekly_activity(filters):
    params = []
    where_clause = _history_where(filters, params)
    return fetch_all(
        f"""
        SELECT DATE(created_at) AS activity_date, COUNT(*) AS request_count
        FROM history
        {where_clause}
        GROUP BY DATE(created_at)
        ORDER BY activity_date ASC
        """,
        tuple(params)
    )


def _get_quiz_performance(filters):
    params = []
    where_clause = _quiz_where(filters, params)
    return fetch_all(
        f"""
        SELECT created_at, topic, percentage
        FROM quiz_attempts
        {where_clause}
        ORDER BY created_at ASC
        """,
        tuple(params)
    )


def _get_study_time(filters):
    quiz_params = []
    quiz_where = _quiz_where(filters, quiz_params)
    quiz_time = fetch_one(
        f"SELECT SUM(time_taken_seconds) AS total_time FROM quiz_attempts {quiz_where}",
        tuple(quiz_params)
    )

    flashcard_params = []
    flashcard_where = _flashcard_where(filters, flashcard_params)
    flashcard_time = fetch_one(
        f"SELECT SUM(study_time_seconds) AS total_time FROM flashcard_sessions {flashcard_where}",
        tuple(flashcard_params)
    )

    return [
        {
            "feature": "Quiz",
            "study_time_seconds": quiz_time["total_time"] or 0 if quiz_time else 0,
        },
        {
            "feature": "Flashcards",
            "study_time_seconds": flashcard_time["total_time"] or 0 if flashcard_time else 0,
        },
    ]


def _get_topic_distribution(filters):
    history_params = []
    history_where = _history_where(filters, history_params)
    quiz_params = []
    quiz_where = _quiz_where(filters, quiz_params)
    flashcard_params = []
    flashcard_where = _flashcard_where(filters, flashcard_params)

    rows = fetch_all(
        f"""
        SELECT topic, COUNT(*) AS topic_count
        FROM (
            SELECT user_prompt AS topic FROM history {history_where}
            UNION ALL
            SELECT topic FROM quiz_attempts {quiz_where}
            UNION ALL
            SELECT topic FROM flashcard_sessions {flashcard_where}
        ) AS topics
        WHERE topic IS NOT NULL AND topic <> ''
        GROUP BY topic
        ORDER BY topic_count DESC, topic ASC
        LIMIT 10
        """,
        tuple(history_params + quiz_params + flashcard_params)
    )

    return rows


def _get_quiz_difficulty(filters):
    params = []
    where_clause = _quiz_where(filters, params)
    return fetch_all(
        f"""
        SELECT difficulty, COUNT(*) AS attempt_count
        FROM quiz_attempts
        {where_clause}
        GROUP BY difficulty
        ORDER BY difficulty ASC
        """,
        tuple(params)
    )


def _get_recent_activity(filters):
    history_params = []
    history_where = _history_where(filters, history_params)
    quiz_params = []
    quiz_where = _quiz_where(filters, quiz_params)
    flashcard_params = []
    flashcard_where = _flashcard_where(filters, flashcard_params)
    pdf_params = []
    pdf_where = _pdf_where(filters, pdf_params)

    return fetch_all(
        f"""
        SELECT feature, topic, activity_date, status
        FROM (
            SELECT feature_name AS feature, user_prompt AS topic, created_at AS activity_date, 'Generated' AS status
            FROM history {history_where}
            UNION ALL
            SELECT 'Quiz Attempts' AS feature, topic, created_at AS activity_date, 'Completed' AS status
            FROM quiz_attempts {quiz_where}
            UNION ALL
            SELECT 'Flashcard Sessions' AS feature, topic, created_at AS activity_date, 'Completed' AS status
            FROM flashcard_sessions {flashcard_where}
            UNION ALL
            SELECT 'PDF Export' AS feature, topic, created_at AS activity_date, 'Exported' AS status
            FROM pdf_exports {pdf_where}
        ) AS activity
        ORDER BY activity_date DESC
        LIMIT 10
        """,
        tuple(history_params + quiz_params + flashcard_params + pdf_params)
    )


def _get_most_active_day(filters):
    rows = _get_weekly_activity(filters)

    if not rows:
        return "None"

    top_row = max(
        rows,
        key=lambda row: row["request_count"]
    )

    return str(top_row["activity_date"])


def _get_weekly_learning_streak(filters):
    rows = _get_weekly_activity(filters)

    if not rows:
        return 0

    return len(
        {
            row["activity_date"]
            for row in rows
        }
    )


def _average_nonzero(values):
    valid_values = [
        value
        for value in values
        if value
    ]

    if not valid_values:
        return 0

    return sum(valid_values) / len(valid_values)
