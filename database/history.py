from database.connection import DatabaseError
from database.queries import delete, fetch_all, fetch_one, insert


def save_history_record(user_id, feature_name, user_prompt, ai_response):
    return insert(
        """
        INSERT INTO history
        (user_id, feature_name, user_prompt, ai_response)
        VALUES (%s, %s, %s, %s)
        """,
        (
            user_id,
            feature_name,
            user_prompt,
            ai_response
        )
    )


def get_recent_history(user_id, limit=5):
    return fetch_all(
        """
        SELECT id, feature_name, user_prompt, ai_response, created_at
        FROM history
        WHERE user_id = %s
        ORDER BY created_at DESC, id DESC
        LIMIT %s
        """,
        (
            user_id,
            limit,
        )
    )


def search_history(user_id, keyword="", feature_name="", history_date=None):
    query = """
        SELECT id, feature_name, user_prompt, ai_response, created_at
        FROM history
        WHERE user_id = %s
    """
    params = [user_id]

    if keyword:
        query += """
            AND (
                user_prompt LIKE %s
                OR ai_response LIKE %s
                OR feature_name LIKE %s
            )
        """
        keyword_pattern = f"%{keyword}%"
        params.extend(
            [
                keyword_pattern,
                keyword_pattern,
                keyword_pattern
            ]
        )

    if feature_name:
        query += " AND feature_name = %s"
        params.append(
            feature_name
        )

    if history_date:
        query += " AND DATE(created_at) = %s"
        params.append(
            history_date
        )

    query += " ORDER BY created_at DESC, id DESC"

    return fetch_all(
        query,
        tuple(params)
    )


def get_history_by_id(user_id, history_id):
    return fetch_one(
        """
        SELECT id, feature_name, user_prompt, ai_response, created_at
        FROM history
        WHERE id = %s AND user_id = %s
        """,
        (
            history_id,
            user_id,
        )
    )


def delete_history_record(user_id, history_id):
    affected_rows = delete(
        """
        DELETE FROM history
        WHERE id = %s AND user_id = %s
        """,
        (
            history_id,
            user_id,
        )
    )

    if affected_rows == 0:
        raise DatabaseError(
            "The selected history record was not found."
        )

    return affected_rows


def delete_all_history(user_id):
    return delete(
        """
        DELETE FROM history
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )


def get_history_statistics(user_id):
    total = fetch_one(
        """
        SELECT COUNT(*) AS total_requests
        FROM history
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    today = fetch_one(
        """
        SELECT COUNT(*) AS today_requests
        FROM history
        WHERE user_id = %s AND DATE(created_at) = CURDATE()
        """,
        (
            user_id,
        )
    )

    most_used = fetch_one(
        """
        SELECT feature_name, COUNT(*) AS usage_count
        FROM history
        WHERE user_id = %s
        GROUP BY feature_name
        ORDER BY usage_count DESC, feature_name ASC
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    return {
        "total_requests": total["total_requests"] if total else 0,
        "today_requests": today["today_requests"] if today else 0,
        "most_used_feature": most_used["feature_name"] if most_used else "None",
    }
