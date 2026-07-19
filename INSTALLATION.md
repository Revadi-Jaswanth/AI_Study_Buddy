# Installation Guide

This guide explains how to install, configure, and run AI Study Buddy on a local machine.

## 1. Install Python

Install Python 3.11 or newer from the official Python website. During installation, enable the option to add Python to PATH.

Verify:

```powershell
python --version
```

## 2. Create a Virtual Environment

From the project folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Install and Configure MySQL

Install MySQL Server and make sure the service is running.

Create a database user or use an existing local user. The app can create the target database automatically through `database.init_db`.

## 5. Configure Environment Variables

Copy the example file:

```powershell
copy .env.example .env
```

Edit `.env`:

```text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=studybuddy_db
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
```

Never commit `.env`.

## 6. Initialize the Database

```powershell
python -m database.init_db
```

This creates the database and all required tables.

## 7. Run the Application

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal.

## 8. Troubleshooting

### Gemini API key missing

Add `GEMINI_API_KEY` to `.env` and restart Streamlit.

### MySQL connection failed

Check that MySQL is running, credentials are correct, and `MYSQL_PORT` is numeric.

### Tables missing

Run:

```powershell
python -m database.init_db
```

### PDF export unavailable

Install dependencies again:

```powershell
pip install -r requirements.txt
```

### Streamlit does not start

Confirm the virtual environment is active and dependencies are installed.
