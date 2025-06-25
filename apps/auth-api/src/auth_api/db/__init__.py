"""Database package for the auth API.

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

__all__ = [
    "check_database_schema",
    "get_db",
    "get_engine",
    "get_session",
    "init_database",
    "init_db",
]
