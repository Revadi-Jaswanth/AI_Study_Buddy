# Database Documentation

AI Study Buddy uses MySQL for persistent storage. Connection details are read only from environment variables.

## Main Tables

### history

Stores successful AI generations.

- `id`
- `feature_name`
- `user_prompt`
- `ai_response`
- `created_at`

### quiz_attempts

Stores interactive quiz attempts.

- `id`
- `topic`
- `difficulty`
- `question_count`
- `score`
- `percentage`
- `time_taken_seconds`
- `created_at`

### flashcard_sessions

Stores flashcard study sessions.

- `id`
- `topic`
- `total_cards`
- `known_cards`
- `revision_cards`
- `completion`
- `study_time_seconds`
- `created_at`

### pdf_exports

Tracks PDF downloads for analytics.

- `id`
- `feature_name`
- `topic`
- `file_name`
- `created_at`

### users

Stores student identity details.

- `id`
- `full_name`
- `email`
- `college_name`
- `branch_department`
- `current_year`
- `created_at`
- `updated_at`

### user_preferences

Stores personalization preferences.

- `id`
- `user_id`
- `education_level`
- `preferred_language`
- `learning_style`
- `exam_type`
- `weak_subjects`
- `daily_study_time`
- `preferred_quiz_difficulty`
- `preferred_flashcard_count`
- `preferred_theme`
- `current_study_goal`
- `exam_date`
- `preferred_explanation_level`

## Database Layer

SQL is kept out of Streamlit pages. Reusable helpers in `database/queries.py` provide:

- `execute_query`
- `fetch_one`
- `fetch_all`
- `insert`
- `update`
- `delete`

## Initialization

Run:

```powershell
python -m database.init_db
```

This creates the database and required tables using `database/schema.sql`.

## Security

- Credentials are loaded from `.env`
- SQL queries use parameters
- User-facing errors are safe
- Logs do not include passwords or API keys
