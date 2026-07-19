from database.queries import fetch_one


def get_student_name(user_id):
    """Retrieve the student's full name by their authenticated user_id."""
    profile_row = fetch_one(
        """
        SELECT full_name
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    if not profile_row:
        return None

    return profile_row["full_name"]
