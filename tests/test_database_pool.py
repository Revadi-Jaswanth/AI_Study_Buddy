import pytest
from unittest.mock import patch, MagicMock
from database.connection import (
    get_connection,
    release_connection,
    transaction,
    health_check,
    DatabaseError,
    _get_pool
)
from database import queries
from mysql.connector import Error as MySQLError


@pytest.fixture(autouse=True)
def clean_singleton_pool():
    # Force reset of the global pool singleton before and after each test
    with patch("database.connection._pool", None):
        yield


def test_pool_singleton_initialization():
    mock_pool = MagicMock()
    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool) as mock_constructor:
        pool1 = _get_pool()
        pool2 = _get_pool()

        # Should only initialize the constructor once
        mock_constructor.assert_called_once()
        assert pool1 is pool2


def test_acquire_and_release_connection():
    mock_conn = MagicMock()
    mock_pool = MagicMock()
    mock_pool.get_connection.return_value = mock_conn

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        conn = get_connection()
        mock_pool.get_connection.assert_called_once()
        assert conn is mock_conn

        release_connection(conn)
        mock_conn.close.assert_called_once()


def test_multiple_connections_can_be_acquired():
    mock_pool = MagicMock()
    mock_pool.get_connection.side_effect = ["conn1", "conn2", "conn3"]

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        c1 = get_connection()
        c2 = get_connection()
        c3 = get_connection()

        assert c1 == "conn1"
        assert c2 == "conn2"
        assert c3 == "conn3"
        assert mock_pool.get_connection.call_count == 3


def test_transaction_commit():
    mock_conn = MagicMock()
    mock_pool = MagicMock()
    mock_pool.get_connection.return_value = mock_conn

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        with transaction() as conn:
            assert conn is mock_conn
            mock_conn.start_transaction.assert_called_once()

        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_conn.close.assert_called_once()


def test_transaction_rollback():
    mock_conn = MagicMock()
    mock_pool = MagicMock()
    mock_pool.get_connection.return_value = mock_conn

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        with pytest.raises(ValueError):
            with transaction():
                mock_conn.start_transaction.assert_called_once()
                raise ValueError("Test rollback trigger")

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        mock_conn.close.assert_called_once()


def test_health_check_healthy():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("studybuddy_db",)
    mock_conn.cursor.return_value = mock_cursor

    mock_pool = MagicMock()
    mock_pool.get_connection.return_value = mock_conn

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        status = health_check()
        assert status["status"] == "healthy"
        assert status["reachable"] is True
        assert status["authenticated"] is True
        assert status["schema_accessible"] is True
        assert status["error"] is None

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_health_check_unhealthy():
    mock_pool = MagicMock()
    mock_pool.get_connection.side_effect = MySQLError("Database connection timed out", 2003)

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        status = health_check()
        assert status["status"] == "unhealthy"
        assert status["reachable"] is False
        assert status["authenticated"] is False
        assert status["schema_accessible"] is False
        assert "Database connection timed out" in status["error"]


def test_query_helpers_fetch_and_execute():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 4
    mock_cursor.lastrowid = 12
    mock_cursor.fetchone.return_value = {"id": 1, "topic": "Pooling"}
    mock_cursor.fetchall.return_value = [{"id": 1, "topic": "Pooling"}]
    mock_conn.cursor.return_value = mock_cursor

    mock_pool = MagicMock()
    mock_pool.get_connection.return_value = mock_conn

    with patch("database.connection.MySQLConnectionPool", return_value=mock_pool):
        # 1. execute_query
        rows = queries.execute_query("UPDATE history SET user_prompt=%s", ("Testing",))
        assert rows == 4
        mock_conn.commit.assert_called_once()

        # 2. fetch_one
        res = queries.fetch_one("SELECT * FROM history LIMIT 1")
        assert res == {"id": 1, "topic": "Pooling"}

        # 3. fetch_all
        res_all = queries.fetch_all("SELECT * FROM history")
        assert res_all == [{"id": 1, "topic": "Pooling"}]

        # 4. insert
        last_id = queries.insert("INSERT INTO history (topic) VALUES (%s)", ("Pooling",))
        assert last_id == 12

        # 5. execute_many
        rows_many = queries.execute_many("INSERT INTO history (topic) VALUES (%s)", [("P1",), ("P2",)])
        assert rows_many == 4
