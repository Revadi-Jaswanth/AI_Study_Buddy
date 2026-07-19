"""Central configuration for AI Study Buddy.

The application reads secrets from environment variables and keeps non-secret
defaults here so feature modules do not hardcode operational settings.
"""

from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


def _env_int(name: str, default: int) -> int:
    """Read an integer environment value with a safe fallback."""
    try:
        return int(os.getenv(name, str(default)))

    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    name: str = "AI Study Buddy"
    page_title: str = "AI Study Buddy"
    page_icon: str = "📚"
    default_theme: str = "dark"


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str | None = os.getenv("GEMINI_API_KEY")
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@dataclass(frozen=True)
class DatabaseConfig:
    host: str | None = os.getenv("MYSQL_HOST")
    port: int = _env_int("MYSQL_PORT", 3306)
    database: str | None = os.getenv("MYSQL_DATABASE")
    user: str | None = os.getenv("MYSQL_USER")
    password: str | None = os.getenv("MYSQL_PASSWORD")


@dataclass(frozen=True)
class ExportConfig:
    pdf_margin: int = 18
    max_filename_length: int = 140
    default_student_name: str | None = None


@dataclass(frozen=True)
class LoggingConfig:
    log_dir: Path = BASE_DIR / "logs"
    log_file: Path = BASE_DIR / "logs" / "app.log"
    level: str = os.getenv("LOG_LEVEL", "INFO")
    max_bytes: int = _env_int("LOG_MAX_BYTES", 1048576)
    backup_count: int = _env_int("LOG_BACKUP_COUNT", 3)


APP_CONFIG = AppConfig()
GEMINI_CONFIG = GeminiConfig()
DATABASE_CONFIG = DatabaseConfig()
EXPORT_CONFIG = ExportConfig()
LOGGING_CONFIG = LoggingConfig()
