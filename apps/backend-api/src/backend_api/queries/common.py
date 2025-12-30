"""
Common utilities, imports, and type definitions for query modules.
"""

from typing import TypeVar

from config.logging import get_logger
from sqlalchemy.engine import Connection
from sqlmodel import Session

# Define a type alias for database sessions that can be either Connection or Session
DBSession = TypeVar("DBSession", Session, Connection)

logger = get_logger(__name__)
