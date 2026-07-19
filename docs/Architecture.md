# Architecture

AI Study Buddy uses a modular Streamlit architecture. The UI entry point is `app.py`, while feature logic, database access, exports, analytics, and profile handling live in dedicated packages.

## High-Level Flow

1. The student selects a feature in the Streamlit sidebar.
2. The feature validates input before processing.
3. Prompt builders in `modules/prompts.py` generate structured Gemini prompts.
4. `modules/gemini_config.py` sends the prompt to Gemini and returns a safe response or friendly error.
5. Successful outputs are saved to MySQL where appropriate.
6. The UI displays results and optional PDF downloads.

## Key Packages

- `modules/`: AI features, prompt generation, quiz and flashcard engines
- `database/`: MySQL connection, schema, initialization, and query helpers
- `analytics/`: dashboard data queries, metrics, charts, and exports
- `exports/`: reusable PDF export system
- `profile/`: student profile, preferences, import/export, and personalization context
- `utils/`: shared utilities such as logging and PDF extraction
- `styles/`: custom Streamlit CSS
- `tests/`: example automated tests
- `docs/`: technical documentation

## Configuration

`config.py` centralizes configurable settings such as app metadata, Gemini model, database values, export limits, and logging settings. Secrets are still read from `.env`.

## Error Handling

Feature modules raise user-safe exceptions. The UI catches those exceptions and displays friendly Streamlit warnings or errors. Internal details are logged to `logs/app.log`.

## Logging

`utils/logging_config.py` configures rotating file logs. Logs include startup, API errors, database errors, and PDF export errors without exposing API keys, passwords, or full user prompts.
