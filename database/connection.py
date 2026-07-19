import os
from contextlib import contextmanager
from dotenv import load_dotenv
from config import DATABASE_CONFIG
from utils.logging_config import get_logger

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    from mysql.connector.pooling import MySQLConnectionPool
except ModuleNotFoundError:
    mysql = None
    MySQLError = Exception
    MySQLConnectionPool = None

load_dotenv()

logger = get_logger(__name__)
_pool = None


class DatabaseError(Exception):
    """Friendly database error for application-level handling."""


def _get_required_env(name):
    config_values = {
        "MYSQL_HOST": DATABASE_CONFIG.host,
        "MYSQL_DATABASE": DATABASE_CONFIG.database,
        "MYSQL_USER": DATABASE_CONFIG.user,
        "MYSQL_PASSWORD": DATABASE_CONFIG.password,
    }
    value = config_values.get(name, os.getenv(name))

    if not value:
        logger.warning("Missing required database setting: %s", name)
        raise DatabaseError(
            f"Missing required database setting: {name}. Please add it to your .env file."
        )

    return value


def get_config(include_database=True):
    config = {
        "host": _get_required_env("MYSQL_HOST"),
        "port": DATABASE_CONFIG.port,
        "user": _get_required_env("MYSQL_USER"),
        "password": _get_required_env("MYSQL_PASSWORD"),
    }

    if include_database:
        config["database"] = _get_required_env("MYSQL_DATABASE")

    return config


def _get_pool():
    """Lazy initialization of the singleton connection pool."""
    global _pool

    if mysql is None or MySQLConnectionPool is None:
        logger.error("mysql-connector-python is not installed.")
        raise DatabaseError(
            "mysql-connector-python is not installed. Run: pip install mysql-connector-python"
        )

    if _pool is None:
        try:
            logger.info("Initializing MySQL Connection Pool: name=studybuddy_pool, size=5")
            _pool = MySQLConnectionPool(
                pool_name="studybuddy_pool",
                pool_size=5,
                **get_config(include_database=True)
            )
        except ValueError as exc:
            logger.exception("Invalid MySQL port configuration.")
            raise DatabaseError(
                "MYSQL_PORT must be a valid number in your .env file."
            ) from exc
        except MySQLError as exc:
            logger.exception("Could not initialize connection pool.")
            raise DatabaseError(
                f"Could not initialize connection pool: {exc}"
            ) from exc

    return _pool


def get_connection():
    """Acquire a pooled connection."""
    pool = _get_pool()
    try:
        conn = pool.get_connection()
        logger.debug("Database connection acquired from pool.")
        return conn
    except MySQLError as exc:
        logger.exception("Failed to acquire connection from pool.")
        raise DatabaseError(
            f"Failed to acquire connection from pool: {exc}"
        ) from exc


def release_connection(connection):
    """Return a pooled connection back to the pool."""
    if connection:
        try:
            connection.close()
            logger.debug("Database connection released back to pool.")
        except MySQLError as exc:
            logger.warning("Failed to release connection back to pool: %s", exc)


def connect():
    """Retrieve a connection from the pool (backward compatibility wrapper)."""
    return get_connection()


def connect_to_server():
    """Acquire a raw, unpooled connection directly to the server (for schema init)."""
    if mysql is None:
        logger.error("mysql-connector-python is not installed.")
        raise DatabaseError(
            "mysql-connector-python is not installed. Run: pip install mysql-connector-python"
        )

    try:
        logger.debug("Establishing direct MySQL server connection.")
        return mysql.connector.connect(
            **get_config(include_database=False)
        )
    except ValueError as exc:
        logger.exception("Invalid MySQL port configuration.")
        raise DatabaseError(
            "MYSQL_PORT must be a valid number in your .env file."
        ) from exc
    except MySQLError as exc:
        logger.exception("Could not connect to MySQL server.")
        raise DatabaseError(
            f"Could not connect to MySQL server: {exc}"
        ) from exc


def close():
    """No-op for backward compatibility (connections are managed by the pool)."""
    pass


@contextmanager
def transaction():
    """Context manager to run queries inside a thread-safe connection transaction."""
    conn = get_connection()
    try:
        conn.start_transaction()
        logger.debug("Transaction started.")
        yield conn
        conn.commit()
        logger.info("Transaction committed successfully.")
    except Exception as exc:
        logger.exception("Transaction failed; rolling back changes.")
        try:
            conn.rollback()
            logger.info("Transaction rolled back successfully.")
        except MySQLError as rb_exc:
            logger.error("Failed to rollback transaction: %s", rb_exc)
        raise exc
    finally:
        release_connection(conn)


def health_check():
    """Perform a database health check verifying connection, auth, and schema access."""
    status = {
        "status": "healthy",
        "reachable": False,
        "authenticated": False,
        "schema_accessible": False,
        "error": None
    }
    conn = None
    cursor = None

    try:
        conn = get_connection()
        status["reachable"] = True
        status["authenticated"] = True

        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()

        if db_name and db_name[0]:
            status["schema_accessible"] = True
        else:
            status["status"] = "degraded"
            status["error"] = "No active database selected."

    except Exception as exc:
        status["status"] = "unhealthy"
        status["error"] = str(exc)
        if "Access denied" in str(exc):
            status["authenticated"] = False
        else:
            status["reachable"] = False

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

    return status
