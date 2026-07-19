from pathlib import Path

from database.connection import (
    DatabaseError,
    MySQLError,
    close,
    connect,
    connect_to_server,
    get_config,
)


def _escape_identifier(identifier):
    return f"`{identifier.replace('`', '``')}`"


def _read_schema():
    schema_path = Path(__file__).with_name("schema.sql")

    if not schema_path.exists():
        raise DatabaseError(
            "schema.sql was not found in the database folder."
        )

    return schema_path.read_text(
        encoding="utf-8"
    )


def _split_sql_statements(sql_script):
    return [
        statement.strip()
        for statement in sql_script.split(";")
        if statement.strip()
    ]


def create_database():
    config = get_config(include_database=True)
    database_name = config["database"]
    server_connection = None
    cursor = None

    try:
        server_connection = connect_to_server()
        cursor = server_connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {_escape_identifier(database_name)} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        server_connection.commit()

    except MySQLError as exc:
        raise DatabaseError(
            f"Could not create MySQL database: {exc}"
        ) from exc

    finally:
        if cursor:
            cursor.close()

        if server_connection and server_connection.is_connected():
            server_connection.close()


def create_tables():
    connection = connect()
    cursor = None

    try:
        cursor = connection.cursor()

        for statement in _split_sql_statements(_read_schema()):
            cursor.execute(statement)

        _migrate_users_table(cursor)
        _migrate_user_id_column(cursor, "history")
        _migrate_user_id_column(cursor, "quiz_attempts")
        _migrate_user_id_column(cursor, "flashcard_progress")
        _migrate_user_id_column(cursor, "flashcard_sessions")
        _migrate_user_id_column(cursor, "study_plans")
        _migrate_user_id_column(cursor, "pdf_exports")

        _migrate_quiz_attempts(cursor)
        _migrate_flashcard_sessions(cursor)
        _migrate_user_preferences(cursor)

        connection.commit()

    except MySQLError as exc:
        connection.rollback()
        raise DatabaseError(
            f"Could not create database tables: {exc}"
        ) from exc

    finally:
        if cursor:
            cursor.close()


def initialize_database():
    create_database()
    create_tables()


def _column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*) AS column_count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
            AND table_name = %s
            AND column_name = %s
        """,
        (
            table_name,
            column_name
        )
    )
    row = cursor.fetchone()

    if isinstance(row, dict):
        return row["column_count"] > 0

    return row[0] > 0


def _migrate_quiz_attempts(cursor):
    migrations = [
        (
            "question_count",
            "ALTER TABLE quiz_attempts ADD COLUMN question_count INT NOT NULL DEFAULT 0 AFTER difficulty"
        ),
        (
            "percentage",
            "ALTER TABLE quiz_attempts ADD COLUMN percentage DECIMAL(5,2) DEFAULT 0.00 AFTER score"
        ),
        (
            "time_taken_seconds",
            "ALTER TABLE quiz_attempts ADD COLUMN time_taken_seconds INT DEFAULT 0 AFTER percentage"
        ),
    ]

    for column_name, statement in migrations:
        if not _column_exists(cursor, "quiz_attempts", column_name):
            cursor.execute(statement)

    if _column_exists(cursor, "quiz_attempts", "questions"):
        cursor.execute(
            "ALTER TABLE quiz_attempts MODIFY questions LONGTEXT NULL"
        )


def _migrate_flashcard_sessions(cursor):
    migrations = [
        (
            "total_cards",
            "ALTER TABLE flashcard_sessions ADD COLUMN total_cards INT NOT NULL DEFAULT 0 AFTER topic"
        ),
        (
            "known_cards",
            "ALTER TABLE flashcard_sessions ADD COLUMN known_cards INT DEFAULT 0 AFTER total_cards"
        ),
        (
            "revision_cards",
            "ALTER TABLE flashcard_sessions ADD COLUMN revision_cards INT DEFAULT 0 AFTER known_cards"
        ),
        (
            "completion",
            "ALTER TABLE flashcard_sessions ADD COLUMN completion DECIMAL(5,2) DEFAULT 0.00 AFTER revision_cards"
        ),
        (
            "study_time_seconds",
            "ALTER TABLE flashcard_sessions ADD COLUMN study_time_seconds INT DEFAULT 0 AFTER completion"
        ),
    ]

    for column_name, statement in migrations:
        if not _column_exists(cursor, "flashcard_sessions", column_name):
            cursor.execute(statement)


def _migrate_user_preferences(cursor):
    migrations = [
        (
            "preferred_quiz_difficulty",
            "ALTER TABLE user_preferences ADD COLUMN preferred_quiz_difficulty VARCHAR(50) DEFAULT 'Medium' AFTER daily_study_time"
        ),
        (
            "preferred_flashcard_count",
            "ALTER TABLE user_preferences ADD COLUMN preferred_flashcard_count INT DEFAULT 10 AFTER preferred_quiz_difficulty"
        ),
        (
            "preferred_theme",
            "ALTER TABLE user_preferences ADD COLUMN preferred_theme VARCHAR(20) DEFAULT 'Dark' AFTER preferred_flashcard_count"
        ),
        (
            "current_study_goal",
            "ALTER TABLE user_preferences ADD COLUMN current_study_goal VARCHAR(255) AFTER preferred_theme"
        ),
        (
            "exam_date",
            "ALTER TABLE user_preferences ADD COLUMN exam_date DATE AFTER current_study_goal"
        ),
        (
            "preferred_explanation_level",
            "ALTER TABLE user_preferences ADD COLUMN preferred_explanation_level VARCHAR(100) DEFAULT 'Beginner' AFTER exam_date"
        ),
    ]

    for column_name, statement in migrations:
        if not _column_exists(cursor, "user_preferences", column_name):
            cursor.execute(statement)


def _migrate_users_table(cursor):
    if not _column_exists(cursor, "users", "password_hash"):
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL")


def _migrate_user_id_column(cursor, table_name):
    if not _column_exists(cursor, table_name, "user_id"):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id INT NULL")
        constraint_name = f"fk_{table_name}_user"
        try:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} "
                f"FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
            )
        except Exception:
            pass


if __name__ == "__main__":
    try:
        initialize_database()
        print("MySQL database initialized successfully.")

    except DatabaseError as exc:
        print(f"Database initialization failed: {exc}")

    finally:
        close()
