"""
Database connection and initialization for survey bot.
Uses psycopg2 with a single PostgreSQL connection per process.
"""

import json
import logging
from datetime import datetime
from typing import Optional

import psycopg2
import psycopg2.extras

from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger("survey-agent")

_conn: Optional[psycopg2.extensions.connection] = None


def get_connection() -> psycopg2.extensions.connection:
    """Return the active connection, (re)connecting if needed."""
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        _conn.autocommit = False
    return _conn


def close_connection() -> None:
    """Close the database connection."""
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
        _conn = None


def insert_call(
    recipient_number: str,
    call_start_time: datetime,
    call_duration_seconds: float,
    completed: bool,
    call_transcript: list,
) -> Optional[int]:
    """
    Insert one call record into the calls table.

    Args:
        recipient_number: Phone number that was called.
        call_start_time: When the call started (datetime).
        call_duration_seconds: Total call length in seconds.
        completed: Whether the survey was completed.
        call_transcript: List of turn dicts
            [{"turn_index": int, "speaker": str, "text": str, "timestamp": str}, ...]

    Returns:
        The new row's id, or None on failure.
    """
    sql = """
        INSERT INTO calls
            (recipient_number, call_start_time, call_duration_seconds, completed, call_transcript)
        VALUES
            (%s, %s, %s, %s, %s)
        RETURNING id
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (
                recipient_number,
                call_start_time,
                round(call_duration_seconds, 2),
                completed,
                json.dumps(call_transcript),
            ))
            row_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Call saved to DB with id={row_id}")
        return row_id
    except Exception as e:
        logger.error(f"Failed to save call to DB: {e}")
        try:
            get_connection().rollback()
        except Exception:
            pass
        return None
