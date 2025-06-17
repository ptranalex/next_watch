"""Database package for the backend API.

This package provides database connectivity and session management.
"""

from .database import (
    check_database_schema,
    get_db,
    get_engine,
    get_session,
    init_database,
    init_db,
)
from .instrumentation import setup_database_instrumentation

__all__ = [
    "check_database_schema",
    "get_db",
    "get_engine",
    "get_session",
    "init_database",
    "init_db",
    "setup_database_instrumentation",
]
