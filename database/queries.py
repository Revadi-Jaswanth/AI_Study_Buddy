from database.connection import (
    DatabaseError,
    MySQLError,
    get_connection,
    release_connection,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


def execute_query(query, params=None):
    """Execute a query (update/delete) and return the number of affected rows."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        logger.debug("execute_query succeeded. Rows affected: %d", cursor.rowcount)
        return cursor.rowcount
    except MySQLError as exc:
        if conn:
            try:
                conn.rollback()
                logger.info("Connection rolled back after query failure.")
            except MySQLError as rb_exc:
                logger.error("Failed to rollback connection: %s", rb_exc)
        logger.exception("Database query execution failed.")
        raise DatabaseError(f"Database query failed: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def execute_many(query, params_list):
    """Execute a query against multiple parameter lists (batch insert/update)."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        logger.debug("execute_many succeeded. Rows affected: %d", cursor.rowcount)
        return cursor.rowcount
    except MySQLError as exc:
        if conn:
            try:
                conn.rollback()
                logger.info("Connection rolled back after executemany failure.")
            except MySQLError as rb_exc:
                logger.error("Failed to rollback connection: %s", rb_exc)
        logger.exception("Database execute_many failed.")
        raise DatabaseError(f"Database query failed: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def fetch_one(query, params=None):
    """Fetch a single row as a dictionary."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except MySQLError as exc:
        logger.exception("Database fetch_one failed.")
        raise DatabaseError(f"Database fetch failed: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def fetch_all(query, params=None):
    """Fetch all rows as a list of dictionaries."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except MySQLError as exc:
        logger.exception("Database fetch_all failed.")
        raise DatabaseError(f"Database fetch failed: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def insert(query, params=None):
    """Insert a record and return the last row ID."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        logger.debug("insert succeeded. Last row ID: %s", last_id)
        return last_id
    except MySQLError as exc:
        if conn:
            try:
                conn.rollback()
                logger.info("Connection rolled back after insert failure.")
            except MySQLError as rb_exc:
                logger.error("Failed to rollback connection: %s", rb_exc)
        logger.exception("Database insert failed.")
        raise DatabaseError(f"Database insert failed: {exc}") from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def update(query, params=None):
    """Update records and return the number of affected rows."""
    return execute_query(query, params)


def delete(query, params=None):
    """Delete records and return the number of affected rows."""
    return execute_query(query, params)
