"""
Shared database connection factory for all microservices.
Each service gets its own connection pool but uses the same PostgreSQL instance.
"""

import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_engines: Dict[str, Engine] = {}


def get_engine(service_name: str = "default") -> Engine:
    """Get or create a SQLAlchemy engine for the given service."""
    if service_name not in _engines:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_user = os.getenv("DB_USER", "pguser")
        db_password = os.getenv("DB_PASSWORD", "root")
        db_name = os.getenv("DB_NAME", "postgres")

        url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        _engines[service_name] = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        logger.info(f"Created DB engine for service: {service_name}")

    return _engines[service_name]


def sql_execute(
    query: str,
    params: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    service_name: str = "default",
) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results as list of dicts.
    Compatible with the existing monolith's sql_execute signature.
    """
    engine = get_engine(service_name)

    with engine.connect() as conn:
        if isinstance(params, list):
            # Batch insert/update
            result = conn.execute(text(query), params)
            conn.commit()
            return []
        else:
            result = conn.execute(text(query), params or {})

            if result.returns_rows:
                rows = result.fetchall()
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                return []
