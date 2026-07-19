import json
import re
from datetime import date, datetime

from profile.profile_database import create_profile, get_active_profile, get_profile_by_email, reset_profile


class ProfileValidationError(Exception):
    """Raised when profile input is invalid."""


def save_profile(user_id, user_data, preferences):
    _validate_user_data(user_data)
    _validate_preferences(preferences)

    existing_email = get_profile_by_email(
        user_data.get("email")
    )
    active_profile = get_active_profile(user_id)

    if existing_email and (
        not active_profile
        or existing_email["id"] != active_profile["user_id"]
    ):
        raise ProfileValidationError(
            "This email is already used by another profile."
        )

    return create_profile(
        user_id,
        user_data,
        preferences
    )


def load_profile(user_id):
    return get_active_profile(user_id)


def delete_profile(user_id):
    return reset_profile(user_id)


def export_profile_json(profile):
    return json.dumps(
        profile or {},
        default=str,
        indent=2
    ).encode("utf-8")


def import_profile_json(raw_json):
    try:
        data = json.loads(raw_json)

    except json.JSONDecodeError as exc:
        raise ProfileValidationError(
            "The imported profile file is not valid JSON."
        ) from exc

    user_data = {
        "full_name": data.get("full_name", ""),
        "email": data.get("email", ""),
        "college_name": data.get("college_name", ""),
        "branch_department": data.get("branch_department", ""),
        "current_year": data.get("current_year", ""),
    }
    try:
        daily_study_time = float(data.get("daily_study_time", 1))
        preferred_flashcard_count = int(data.get("preferred_flashcard_count", 10))

    except (TypeError, ValueError) as exc:
        raise ProfileValidationError(
            "Imported study time and flashcard count must be valid numbers."
        ) from exc

    preferences = {
        "education_level": data.get("education_level", "Beginner"),
        "preferred_language": data.get("preferred_language", "English"),
        "learning_style": data.get("learning_style", "Mixed"),
        "exam_type": data.get("exam_type", "Semester"),
        "weak_subjects": data.get("weak_subjects", ""),
        "daily_study_time": daily_study_time,
        "preferred_quiz_difficulty": data.get("preferred_quiz_difficulty", "Medium"),
        "preferred_flashcard_count": preferred_flashcard_count,
        "preferred_theme": data.get("preferred_theme", "Dark"),
        "current_study_goal": data.get("current_study_goal", ""),
        "exam_date": _parse_optional_date(data.get("exam_date")),
        "preferred_explanation_level": data.get("preferred_explanation_level", "Beginner"),
    }

    return save_profile(
        user_data,
        preferences
    )


def _validate_user_data(user_data):
    required_fields = [
        "full_name",
        "college_name",
        "branch_department",
        "current_year",
    ]

    for field in required_fields:
        if not str(user_data.get(field, "")).strip():
            raise ProfileValidationError(
                f"{field.replace('_', ' ').title()} is required."
            )

    email = user_data.get("email")

    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ProfileValidationError(
            "Please enter a valid email address."
        )


def _validate_preferences(preferences):
    daily_study_time = float(preferences.get("daily_study_time", 0))

    if daily_study_time <= 0 or daily_study_time > 24:
        raise ProfileValidationError(
            "Daily study time must be between 0 and 24 hours."
        )

    flashcard_count = int(preferences.get("preferred_flashcard_count", 0))

    if flashcard_count not in [5, 10, 15, 20]:
        raise ProfileValidationError(
            "Preferred flashcard count must be 5, 10, 15, or 20."
        )


def _parse_optional_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).date()

    except ValueError as exc:
        raise ProfileValidationError(
            "Imported exam date must use YYYY-MM-DD format."
        ) from exc
