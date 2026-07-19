from database.connection import DatabaseError
from database.queries import delete, fetch_all, fetch_one, insert


def save_quiz_attempt(user_id, topic, difficulty, question_count, score, percentage, time_taken_seconds):
    return insert(
        """
        INSERT INTO quiz_attempts
        (user_id, topic, difficulty, question_count, score, percentage, time_taken_seconds)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            topic,
            difficulty,
            question_count,
            score,
            percentage,
            time_taken_seconds
        )
    )


def get_quiz_attempts(user_id, keyword="", sort_by="Date Desc"):
    query = """
        SELECT id, topic, difficulty, question_count, score, percentage,
            time_taken_seconds, created_at
        FROM quiz_attempts
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
        "Score Desc": "percentage DESC, created_at DESC",
        "Score Asc": "percentage ASC, created_at DESC",
    }
    query += f" ORDER BY {sort_options.get(sort_by, sort_options['Date Desc'])}"

    return fetch_all(
        query,
        tuple(params)
    )


def delete_quiz_attempt(user_id, attempt_id):
    affected_rows = delete(
        """
        DELETE FROM quiz_attempts
        WHERE id = %s AND user_id = %s
        """,
        (
            attempt_id,
            user_id,
        )
    )

    if affected_rows == 0:
        raise DatabaseError(
            "The selected quiz attempt was not found."
        )

    return affected_rows


def get_quiz_analytics(user_id):
    highest = fetch_one(
        """
        SELECT MAX(percentage) AS highest_score
        FROM quiz_attempts
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    average = fetch_one(
        """
        SELECT AVG(percentage) AS average_score
        FROM quiz_attempts
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    best_topic = fetch_one(
        """
        SELECT topic, AVG(percentage) AS average_percentage
        FROM quiz_attempts
        WHERE user_id = %s
        GROUP BY topic
        ORDER BY average_percentage DESC, topic ASC
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    most_attempted = fetch_one(
        """
        SELECT topic, COUNT(*) AS attempt_count
        FROM quiz_attempts
        WHERE user_id = %s
        GROUP BY topic
        ORDER BY attempt_count DESC, topic ASC
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    return {
        "highest_score": round(highest["highest_score"] or 0, 2) if highest else 0,
        "average_score": round(average["average_score"] or 0, 2) if average else 0,
        "best_topic": best_topic["topic"] if best_topic else "None",
        "most_attempted_topic": most_attempted["topic"] if most_attempted else "None",
    }
