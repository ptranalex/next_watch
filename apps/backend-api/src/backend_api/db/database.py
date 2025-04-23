"""
Database connection module for the backend API.
"""

import os
from contextlib import contextmanager
from sqlmodel import Session
from movie_storage.db import init_db, get_engine, get_session
from movie_storage.config.app import Config

***REMOVED*** Database URL from environment variable with a PostgreSQL default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://alex:postgres@localhost:5432/next_watch"
)

***REMOVED*** SQL Echo setting for debugging
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"


***REMOVED*** Initialize database on startup
def init_database():
    """Initialize the database connection using movie-storage."""
    ***REMOVED*** In production, you may want to set create_tables=False
    ***REMOVED*** and manage migrations separately with alembic

    ***REMOVED*** Create config with echo setting
    config = Config()
    config.database_url = DATABASE_URL
    config.database_echo = SQL_ECHO

    ***REMOVED*** Initialize database with config
    init_db(db_url=DATABASE_URL, create_tables=True, config=config)


***REMOVED*** Dependency to use in routes
def get_db():
    """Get a database session for use in API endpoints."""
    session_generator = get_session()
    try:
        db = next(session_generator)
        yield db
    finally:
        try:
            next(session_generator)
        except StopIteration:
            pass
