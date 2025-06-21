"""Dependency injection helpers for FastAPI applications.

This module provides common dependency providers for FastAPI applications,
including authentication, caching, database, and other service dependencies.
"""

from typing import Any

from config.logging import get_logger

logger = get_logger(__name__)

***REMOVED*** Available dependencies - will be populated as modules are imported
__all__ = []

***REMOVED*** Common dependencies
try:
    from .common import get_pagination, get_request_id, get_search_params, get_settings

    __all__.extend(["get_settings", "get_request_id", "get_pagination", "get_search_params"])
except ImportError as e:
    logger.debug(f"Common dependencies not available: {e}")

***REMOVED*** Auth dependencies
try:
    from .auth import get_api_key, get_current_user, get_optional_user, require_auth

    __all__.extend(["get_api_key", "get_current_user", "require_auth", "get_optional_user"])
except ImportError as e:
    logger.debug(f"Auth dependencies not available: {e}")

***REMOVED*** Cache dependencies
try:
    from .cache import (
        CacheService,
        get_cache_decorator,
        get_cache_manager,
        get_cache_provider,
        get_cache_service,
        get_redis_client,
    )

    __all__.extend(
        [
            "get_cache_manager",
            "get_cache_provider",
            "get_redis_client",
            "get_cache_decorator",
            "get_cache_service",
            "CacheService",
        ]
    )
except ImportError as e:
    logger.debug(f"Cache dependencies not available: {e}")

***REMOVED*** Database dependencies
try:
    from .database import (
        DatabaseService,
        get_database_engine,
        get_database_service,
        get_db_session,
        get_db_transaction,
        get_read_only_session,
    )

    __all__.extend(
        [
            "get_db_session",
            "get_db_transaction",
            "get_database_engine",
            "get_database_service",
            "get_read_only_session",
            "DatabaseService",
        ]
    )
except ImportError as e:
    logger.debug(f"Database dependencies not available: {e}")
