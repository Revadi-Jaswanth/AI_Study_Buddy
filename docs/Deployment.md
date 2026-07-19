# Deployment Guide

This document outlines deployment options for AI Study Buddy.

## GitHub

1. Ensure `.env` is ignored.
2. Add `.env.example`, README, installation guide, and docs.
3. Commit the project.
4. Push to GitHub.

Do not upload local databases, virtual environments, logs, or API keys.

## Streamlit Community Cloud

Streamlit Community Cloud is suitable for the Streamlit app, but MySQL must be hosted separately.

Steps:

1. Push the project to GitHub.
2. Create a Streamlit Community Cloud app from the repository.
3. Set the main file to `app.py`.
4. Add environment variables through Streamlit secrets or the deployment settings.
5. Configure a reachable MySQL host.

## MySQL Hosting

Use a hosted MySQL provider for deployment. Update environment variables:

```text
MYSQL_HOST=YOUR_HOST
MYSQL_PORT=3306
MYSQL_DATABASE=YOUR_DATABASE
MYSQL_USER=YOUR_USER
MYSQL_PASSWORD=YOUR_PASSWORD
```

Run the initialization script from a trusted environment that can reach the database:

```powershell
python -m database.init_db
```

## Environment Variables

Required:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`

Optional:

- `LOG_LEVEL`
- `LOG_MAX_BYTES`
- `LOG_BACKUP_COUNT`

## Production Notes

- Use strong database credentials
- Restrict database network access
- Rotate API keys if exposed
- Avoid logging sensitive user content
- Add authentication before supporting multiple real users
