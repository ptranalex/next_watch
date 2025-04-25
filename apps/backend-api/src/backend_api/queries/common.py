"""
Common utilities, imports, and type definitions for query modules.
"""

from sqlalchemy.sql import text
from typing import List, Tuple, Dict, Any, Optional, Union, Sequence, cast, TypeVar
from datetime import datetime
import logging
from sqlalchemy.engine import Connection
from sqlmodel import Session

***REMOVED*** Define a type alias for database sessions that can be either Connection or Session
DBSession = TypeVar("DBSession", Session, Connection)

logger = logging.getLogger(__name__)
