from database.connection import DatabaseError
from database.queries import delete, fetch_one, insert, update


def get_active_profile(user_id):
    """Retrieve user details and preferences by user_id."""
    return fetch_one(
        """
        SELECT
            u.id AS user_id,
            u.full_name,
            u.email,
            u.college_name,
            u.branch_department,
            u.current_year,
            p.education_level,
            p.preferred_language,
            p.learning_style,
            p.exam_type,
            p.weak_subjects,
            p.daily_study_time,
            p.preferred_quiz_difficulty,
            p.preferred_flashcard_count,
            p.preferred_theme,
            p.current_study_goal,
            p.exam_date,
            p.preferred_explanation_level
        FROM users u
        LEFT JOIN user_preferences p ON p.user_id = u.id
        WHERE u.id = %s
        """,
        (user_id,)
    )


def get_profile_by_email(email):
    if not email:
        return None

    return fetch_one(
        """
        SELECT id
        FROM users
        WHERE email = %s
        """,
        (
            email,
        )
    )


def create_profile(user_id, user_data, preferences):
    """Update a user's details and preferences."""
    return update_profile(
        user_id,
        user_data,
        preferences
    )


def update_profile(user_id, user_data, preferences):
    affected_rows = update(
        """
        UPDATE users
        SET full_name = %s,
            email = %s,
            college_name = %s,
            branch_department = %s,
            current_year = %s
        WHERE id = %s
        """,
        (
            user_data["full_name"],
            user_data.get("email") or None,
            user_data["college_name"],
            user_data["branch_department"],
            user_data["current_year"],
            user_id,
        )
    )

    existing_preferences = fetch_one(
        """
        SELECT id
        FROM user_preferences
        WHERE user_id = %s
        """,
        (
            user_id,
        )
    )

    if existing_preferences:
        update(
            """
            UPDATE user_preferences
            SET education_level = %s,
                preferred_language = %s,
                learning_style = %s,
                exam_type = %s,
                weak_subjects = %s,
                daily_study_time = %s,
                preferred_quiz_difficulty = %s,
                preferred_flashcard_count = %s,
                preferred_theme = %s,
                current_study_goal = %s,
                exam_date = %s,
                preferred_explanation_level = %s
            WHERE user_id = %s
            """,
            _preference_params(preferences) + (
                user_id,
            )
        )
    else:
        _insert_preferences(
            user_id,
            preferences
        )

    return user_id


def reset_profile(user_id):
    """Delete a user account and all cascading records."""
    return delete(
        """
        DELETE FROM users
        WHERE id = %s
        """,
        (
            user_id,
        )
    )


def _insert_preferences(user_id, preferences):
    return insert(
        """
        INSERT INTO user_preferences
        (
            user_id,
            education_level,
            preferred_language,
            learning_style,
            exam_type,
            weak_subjects,
            daily_study_time,
            preferred_quiz_difficulty,
            preferred_flashcard_count,
            preferred_theme,
            current_study_goal,
            exam_date,
            preferred_explanation_level
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            *_preference_params(preferences)
        )
    )


def _preference_params(preferences):
    return (
        preferences["education_level"],
        preferences["preferred_language"],
        preferences["learning_style"],
        preferences["exam_type"],
        preferences.get("weak_subjects") or "",
        preferences["daily_study_time"],
        preferences["preferred_quiz_difficulty"],
        preferences["preferred_flashcard_count"],
        preferences["preferred_theme"],
        preferences.get("current_study_goal") or "",
        preferences.get("exam_date") or None,
        preferences["preferred_explanation_level"],
    )
