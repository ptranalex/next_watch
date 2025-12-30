"""Cache key building utilities."""

import hashlib
from abc import ABC, abstractmethod
from typing import Any, cast


class CacheKeyBuilder(ABC):
    """Abstract base class for cache key builders."""

    @abstractmethod
    def build(self) -> str:
        """Build the cache key string."""
        pass

    @abstractmethod
    def namespace(self) -> str:
        """Get the namespace for this key type."""
        pass

    def full_key(self, prefix: str = "nextwatch") -> str:
        """Build the full cache key with namespace and prefix."""
        return f"{prefix}:{self.namespace()}:{self.build()}"


def build_cache_key(
    namespace: str, key_parts: list[str | int | None], prefix: str = "nextwatch"
) -> str:
    """Build a cache key from namespace and parts.

    Args:
        namespace: The cache namespace (e.g., 'movie', 'user')
        key_parts: List of key components
        prefix: Global key prefix

    Returns:
        Formatted cache key string

    Example:
        >>> build_cache_key("movie", ["details", 123, "user", 456])
        "nextwatch:movie:details:123:user:456"
    """
    # Filter out None values and convert to strings
    clean_parts = [str(part) for part in key_parts if part is not None]
    key_string = ":".join(clean_parts)
    return f"{prefix}:{namespace}:{key_string}"


def hash_parameters(params: dict[str, Any], length: int = 8) -> str:
    """Create a short hash from parameters dictionary.

    Useful for creating cache keys from complex parameter sets.

    Args:
        params: Dictionary of parameters
        length: Length of the resulting hash

    Returns:
        Short hash string

    Example:
        >>> hash_parameters({"genre": 1, "year": 2023, "rating": 8.5})
        "a1b2c3d4"
    """
    # Create a consistent string representation
    param_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)

    # Generate MD5 hash and truncate
    hash_obj = hashlib.md5(param_string.encode())
    return hash_obj.hexdigest()[:length]


def build_filtered_key(
    base_namespace: str,
    base_id: str | int,
    filters: dict[str, Any],
    user_id: str | int | None = None,
    prefix: str = "nextwatch",
) -> str:
    """Build a cache key for filtered data.

    Useful for endpoints with many optional filters.

    Args:
        base_namespace: Base namespace (e.g., 'genre', 'actor')
        base_id: Primary identifier
        filters: Dictionary of filter parameters
        user_id: Optional user identifier
        prefix: Global key prefix

    Returns:
        Cache key with hashed filter parameters

    Example:
        >>> build_filtered_key("genre", 1, {"year": 2023, "rating": 8.5}, user_id=123)
        "nextwatch:genre:1:filters:a1b2c3d4:user:123"
    """
    # Hash the filters for a consistent, short key
    filter_hash = hash_parameters(filters)

    # Build key parts
    key_parts: list[str | int | None] = [str(base_id), "filters", filter_hash]

    if user_id is not None:
        key_parts.extend(["user", str(user_id)])

    return build_cache_key(base_namespace, key_parts, prefix)


def build_paginated_key(
    namespace: str,
    base_parts: list[str | int],
    page: int,
    limit: int,
    user_id: str | int | None = None,
    prefix: str = "nextwatch",
) -> str:
    """Build a cache key for paginated data.

    Args:
        namespace: Cache namespace
        base_parts: Base key components
        page: Page number
        limit: Items per page
        user_id: Optional user identifier
        prefix: Global key prefix

    Returns:
        Cache key for paginated data

    Example:
        >>> build_paginated_key("actor", [123, "movies"], 2, 20, user_id=456)
        "nextwatch:actor:123:movies:page:2:limit:20:user:456"
    """
    key_parts: list[str | int | None] = cast(
        list[str | int | None],
        [str(part) for part in base_parts]
        + [
            "page",
            str(page),
            "limit",
            str(limit),
        ],
    )

    if user_id is not None:
        key_parts.extend(["user", str(user_id)])

    return build_cache_key(namespace, key_parts, prefix)
