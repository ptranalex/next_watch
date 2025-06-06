"""
Common utilities, imports, and type definitions for query modules.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, TypeVar, Union, cast

from sqlalchemy.engine import Connection
from sqlalchemy.sql import text
from sqlmodel import Session

***REMOVED*** Define a type alias for database sessions that can be either Connection or Session
DBSession = TypeVar("DBSession", Session, Connection)

logger = logging.getLogger(__name__)
