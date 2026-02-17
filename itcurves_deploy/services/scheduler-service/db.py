"""
Database operations for the Scheduler Service.
Reads/Writes: campaigns, surveys, job_history.
"""

import os
import logging
from typing import Any, Dict, List, Union

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_user = os.getenv("DB_USER", "pguser")
        db_password = os.getenv("DB_PASSWORD", "root")
        url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/db"
        _engine = create_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    return _engine


def sql_execute(query: str, params: Union[dict, List[dict], None] = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query. For SELECT: returns list of dicts.
    For mutations: commits and returns empty list.
    """
    engine = get_engine()
    with engine.connect() as conn:
        if isinstance(params, list):
            result = conn.execute(text(query), params)
            conn.commit()
            return []
        result = conn.execute(text(query), params or {})
        if result.returns_rows:
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
        conn.commit()
        return []
