from database.connection import DatabaseError
from database.queries import delete, fetch_all, fetch_one, insert


def save_flashcard_session(user_id, topic, total_cards, known_cards, revision_cards, completion, study_time_seconds):
    return insert(
        """
        INSERT INTO flashcard_sessions
        (user_id, topic, total_cards, known_cards, revision_cards, completion, study_time_seconds)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            topic,
            total_cards,
            known_cards,
            revision_cards,
            completion,
            study_time_seconds
        )
    )


def get_flashcard_sessions(user_id, keyword="", sort_by="Date Desc"):
    query = """
        SELECT id, topic, total_cards, known_cards, revision_cards,
            completion, study_time_seconds, created_at
        FROM flashcard_sessions
        WHERE user_id = %s
    """
    params = [user_id]

    if keyword:
        query += " AND topic LIKE %s"
        params.append(
            f"%{keyword}%"
        )

    sort_options = {
        "Date Desc": "created_at DESC, id DESC",
        "Date Asc": "created_at ASC, id ASC",
        "Completion Desc": "completion DESC, created_at DESC",
        "Completion Asc": "completion ASC, created_at DESC",
    }
    query += f" ORDER BY {sort_options.get(sort_by, sort_options['Date Desc'])}"

    return fetch_all(
        query,
        tuple(params)
    )


def get_flashcard_session(user_id, session_id):
    return fetch_one(
        """
        SELECT id, topic, total_cards, known_cards, revision_cards,
            completion, study_time_seconds, created_at
        FROM flashcard_sessions
        WHERE id = %s AND user_id = %s
        """,
        (
            session_id,
            user_id,
        )
    )


def delete_flashcard_session(user_id, session_id):
    affected_rows = delete(
        """
        DELETE FROM flashcard_sessions
        WHERE id = %s AND user_id = %s
        """,
        (
            session_id,
            user_id,
        )
    )

    if affected_rows == 0:
        raise DatabaseError(
            "The selected flashcard session was not found."
        )

    return affected_rows


def get_flashcard_analytics(user_id):
    total = fetch_one(
        """
        SELECT COUNT(*) AS total_sessions
        FROM flashcard_sessions
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    average_completion = fetch_one(
        """
        SELECT AVG(completion) AS average_completion
        FROM flashcard_sessions
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    average_mastery = fetch_one(
        """
        SELECT AVG((known_cards / NULLIF(total_cards, 0)) * 100) AS average_mastery
        FROM flashcard_sessions
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    most_studied = fetch_one(
        """
        SELECT topic, COUNT(*) AS session_count
        FROM flashcard_sessions
        WHERE user_id = %s
        GROUP BY topic
        ORDER BY session_count DESC, topic ASC
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    return {
        "total_sessions": total["total_sessions"] if total else 0,
        "average_completion": round(average_completion["average_completion"] or 0, 2)
        if average_completion else 0,
        "average_mastery": round(average_mastery["average_mastery"] or 0, 2)
        if average_mastery else 0,
        "most_studied_topic": most_studied["topic"] if most_studied else "None",
    }
