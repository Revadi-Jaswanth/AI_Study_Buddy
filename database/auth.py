import bcrypt
from database.connection import DatabaseError, transaction
from database.queries import fetch_one, insert, update, delete
from utils.logging_config import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as exc:
        logger.error("Failed to check password: %s", exc)
        return False


def register_user(full_name, email, password, college_name, branch_department, current_year):
    """Register a new user and initialize their default preferences inside a transaction."""
    email = str(email).strip().lower()
    full_name = str(full_name).strip()

    if not email or not password or not full_name:
        raise DatabaseError("Name, email, and password are required fields.")

    # Check if email is already taken
    existing = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
    if existing:
        raise DatabaseError("This email address is already registered.")

    password_hash = hash_password(password)

    try:
        with transaction() as conn:
            cursor = conn.cursor()
            # 1. Insert user
            cursor.execute(
                """
                INSERT INTO users
                (full_name, email, password_hash, college_name, branch_department, current_year)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    full_name,
                    email,
                    password_hash,
                    college_name,
                    branch_department,
                    current_year,
                )
            )
            user_id = cursor.lastrowid

            # 2. Insert default preferences
            cursor.execute(
                """
                INSERT INTO user_preferences
                (
                    user_id, education_level, preferred_language, learning_style,
                    exam_type, weak_subjects, daily_study_time, preferred_quiz_difficulty,
                    preferred_flashcard_count, preferred_theme, current_study_goal,
                    exam_date, preferred_explanation_level
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    "Beginner",
                    "English",
                    "Mixed",
                    "Semester",
                    "",
                    1.00,
                    "Medium",
                    10,
                    "Dark",
                    "",
                    None,
                    "Beginner",
                )
            )

            logger.info("User registered successfully: id=%d, email=%s", user_id, email)
            return user_id

    except Exception as exc:
        logger.exception("User registration transaction failed.")
        raise DatabaseError(f"User registration failed: {exc}") from exc


def authenticate_user(email, password):
    """Authenticate a user by checking their password hash. Returns user dict on success."""
    email = str(email).strip().lower()

    if not email or not password:
        return None

    try:
        user = fetch_one(
            """
            SELECT id, full_name, email, password_hash, college_name, branch_department, current_year
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        if user and check_password(password, user["password_hash"]):
            logger.info("User authenticated successfully: id=%d", user["id"])
            # Remove hash before returning user details
            user.pop("password_hash", None)
            return user

        logger.warning("Authentication failed for email: %s", email)
        return None

    except Exception as exc:
        logger.exception("Database error during user authentication.")
        raise DatabaseError(f"Authentication database failure: {exc}") from exc


def change_user_password(user_id, old_password, new_password):
    """Update a user's password after validating their old password."""
    if not new_password or len(str(new_password).strip()) < 6:
        raise DatabaseError("New password must be at least 6 characters long.")

    user = fetch_one("SELECT password_hash FROM users WHERE id = %s", (user_id,))
    if not user:
        raise DatabaseError("User account not found.")

    if not check_password(old_password, user["password_hash"]):
        raise DatabaseError("Current password incorrect.")

    new_hash = hash_password(new_password)
    affected = update("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
    logger.info("Password updated successfully for user_id=%d", user_id)
    return affected > 0


def delete_user_account(user_id):
    """Delete a user account and all cascading records (managed by foreign keys cascade)."""
    affected = delete("DELETE FROM users WHERE id = %s", (user_id,))
    if affected == 0:
        raise DatabaseError("User account not found.")
    logger.info("User account and all cascading records deleted for user_id=%d", user_id)
    return affected > 0
