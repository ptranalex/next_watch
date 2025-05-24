"""
Database connection module for the auth API.
"""

from sqlmodel import Session
from movie_storage.db import init_db, get_session
from movie_storage.config.app import Config
from auth_api.config.app import settings


def init_database():
    """Initialize the database connection using movie-storage."""
    ***REMOVED*** Create config for movie-storage compatibility
    config = Config()
    config.database_url = settings.database_url

    ***REMOVED*** Initialize database with config
    ***REMOVED*** For auth service, we don't need to create tables as they're managed centrally
    init_db(db_url=settings.database_url, create_tables=False, config=config)


def get_db():
    """Get a database session for use in auth API endpoints."""
    session_generator = get_session()
    try:
        db = next(session_generator)
        yield db
    finally:
        try:
            next(session_generator)
        except StopIteration:
            pass
