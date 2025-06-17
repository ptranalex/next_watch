"""
Common utilities, imports, and type definitions for query modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, TypeVar, Union, cast

from sqlalchemy.engine import Connection
from sqlalchemy.sql import text
from sqlmodel import Session

from backend_api.config.logging import get_logger

***REMOVED*** Define a type alias for database sessions that can be either Connection or Session
DBSession = TypeVar("DBSession", Session, Connection)

logger = get_logger(__name__)
