import pytest
from unittest.mock import patch, MagicMock
from database import auth
from database.connection import DatabaseError


def test_password_hashing_and_verification():
    password = "SuperSecretPassword123"
    hashed = auth.hash_password(password)

    assert hashed != password
    assert auth.check_password(password, hashed) is True
    assert auth.check_password("WrongPassword", hashed) is False


@patch("database.auth.fetch_one")
@patch("database.auth.transaction")
def test_register_user_success(mock_transaction, mock_fetch_one):
    # No existing user
    mock_fetch_one.return_value = None

    # Mock cursor and transaction context manager
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42
    mock_conn.cursor.return_value = mock_cursor

    # Make the context manager yield our mock connection
    mock_transaction.return_value.__enter__.return_value = mock_conn

    user_id = auth.register_user(
        "John Doe",
        "john@example.com",
        "password123",
        "State College",
        "Engineering",
        "Third Year"
    )

    assert user_id == 42
    mock_fetch_one.assert_called_once()
    mock_cursor.execute.assert_called()


@patch("database.auth.fetch_one")
def test_register_user_email_taken(mock_fetch_one):
    # User already exists
    mock_fetch_one.return_value = {"id": 1}

    with pytest.raises(DatabaseError) as exc_info:
        auth.register_user(
            "John Doe",
            "john@example.com",
            "password123",
            "State College",
            "Engineering",
            "Third Year"
        )

    assert "already registered" in str(exc_info.value)


@patch("database.auth.fetch_one")
def test_authenticate_user_success(mock_fetch_one):
    hashed_pass = auth.hash_password("mypassword")
    mock_fetch_one.return_value = {
        "id": 10,
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "password_hash": hashed_pass,
        "college_name": "MIT",
        "branch_department": "CS",
        "current_year": "Final Year",
    }

    user = auth.authenticate_user("alice@example.com", "mypassword")
    assert user is not None
    assert user["id"] == 10
    assert user["full_name"] == "Alice Smith"
    assert "password_hash" not in user


@patch("database.auth.fetch_one")
def test_authenticate_user_failure(mock_fetch_one):
    hashed_pass = auth.hash_password("mypassword")
    mock_fetch_one.return_value = {
        "id": 10,
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "password_hash": hashed_pass,
        "college_name": "MIT",
        "branch_department": "CS",
        "current_year": "Final Year",
    }

    # Wrong password
    user = auth.authenticate_user("alice@example.com", "wrongpassword")
    assert user is None


@patch("database.auth.fetch_one")
@patch("database.auth.update")
def test_change_user_password_success(mock_update, mock_fetch_one):
    hashed_pass = auth.hash_password("oldpassword")
    mock_fetch_one.return_value = {"password_hash": hashed_pass}
    mock_update.return_value = 1

    success = auth.change_user_password(10, "oldpassword", "newpassword123")
    assert success is True
    mock_update.assert_called_once()


@patch("database.auth.delete")
def test_delete_user_account(mock_delete):
    mock_delete.return_value = 1
    success = auth.delete_user_account(10)
    assert success is True
    mock_delete.assert_called_once_with("DELETE FROM users WHERE id = %s", (10,))
