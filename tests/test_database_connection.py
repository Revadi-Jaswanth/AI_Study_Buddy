import pytest

from database.connection import DatabaseError, _get_required_env


def test_required_env_reports_missing_value(monkeypatch):
    monkeypatch.delenv(
        "NOT_A_REAL_SETTING",
        raising=False,
    )

    with pytest.raises(DatabaseError):
        _get_required_env("NOT_A_REAL_SETTING")
