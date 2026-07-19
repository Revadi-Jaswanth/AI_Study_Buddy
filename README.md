# AI Study Buddy

AI Study Buddy is a professional Streamlit-based learning platform powered by Google Gemini and MySQL. It helps students explain topics, summarize notes, practice interactive quizzes, study flashcards, generate study plans, solve doubts, export PDFs, track history, view analytics, and personalize AI responses through a student profile.

## Features

- Professional dark-first Streamlit interface
- Gemini-powered topic explanation, notes summary, planner, and doubt solving
- Interactive quiz system with scoring, review, history, analytics, and PDF export
- Interactive flashcard learning with progress tracking and weak-card review
- MySQL-backed study history, quiz attempts, flashcard sessions, profile, and analytics
- PDF export for generated study material
- Student profile and AI personalization
- Analytics dashboard with Plotly charts
- Centralized configuration and reusable logging

## Technology Stack

- Python
- Streamlit
- Google Gemini API
- MySQL
- mysql-connector-python
- fpdf2
- Plotly
- python-dotenv
- pytest

## Folder Structure

```text
AI_Study_Buddy/
  app.py
  config.py
  requirements.txt
  .env.example
  README.md
  INSTALLATION.md
  assets/
  styles/
  database/
  modules/
  analytics/
  exports/
  profile/
  utils/
  logs/
  tests/
  docs/
```

## Installation

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with your Gemini API key and MySQL credentials.

## Database Setup

Create and initialize the MySQL database:

```powershell
python -m database.init_db
```

## Running the Application

```powershell
streamlit run app.py
```

## Environment Variables

See [.env.example](.env.example) for all required placeholders.

## Screenshots

Add screenshots in the `assets/` folder before final submission:

- Landing dashboard
- Topic explainer
- Interactive quiz
- Flashcard player
- Analytics dashboard
- Student profile

## Testing

```powershell
pytest
```

The included tests are lightweight examples for core logic and can be expanded as the project grows.

## Future Enhancements

- User authentication
- Multi-user profile switching
- Cloud database deployment
- Email reminders
- Spaced repetition scheduling
- Admin analytics

## License

This project is prepared for academic and internship portfolio use. Add a formal license before public distribution.
