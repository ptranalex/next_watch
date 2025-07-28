"""
Redis-backed search suggestion service.

This module provides a comprehensive suggestion engine that was moved from backend-api
to the dedicated search-api service. It supports advanced features like:
- Prefix matching with Redis sorted sets
- Entity-based suggestions with metadata
- Ranking and deduplication
- Fuzzy matching fallbacks
"""

import json
import math
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import redis.asyncio
from redis.exceptions import RedisError
import asyncio

from config.logging import get_logger
from fast_core.errors import optional_service_handler, critical_service_handler

logger = get_logger(__name__)

***REMOVED*** TMDB image base URLs for different sizes
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


class SuggestionEngine:
    """
    A service for retrieving search suggestions from Redis.

    This implementation supports prefix matching using sorted sets in Redis.
    It can be easily extended to support other mechanisms like ZSCAN or ZRANGEBYLEX
    depending on how your suggestions are stored in Redis.
    """

    def __init__(
        self,
        redis_url: str,
        max_connections: int = 10,
        suggestion_key_prefix: str = "suggestions:",
        entity_key_prefix: str = "entity:",
        search_result_prefix: str = "search_results:",
        entity_types: Optional[List[str]] = None,
    ):
        """
        Initialize the suggestion engine with Redis connection parameters.

        Args:
            redis_url: Redis connection URL in format redis://host:port/db
            max_connections: Maximum number of Redis connections in the pool
            suggestion_key_prefix: Redis key prefix for suggestions (default: "suggestions:")
            entity_key_prefix: Redis key prefix for entities (default: "entity:")
            search_result_prefix: Redis key prefix for search results (default: "search_results:")
            entity_types: List of entity types to search (default: ["movie", "actor", "director"])
        """
        self._redis_url = redis_url
        self._pool: Optional[redis.asyncio.ConnectionPool] = None  ***REMOVED*** type: ignore
        self._max_connections = max_connections
        self._suggestion_key_prefix = suggestion_key_prefix
        self._entity_key_prefix = entity_key_prefix
        self._search_result_prefix = search_result_prefix
        self._entity_types = entity_types or ["movie", "actor", "director"]

    @critical_service_handler("redis", logger)
    async def initialize(self) -> None:
        """
        Initialize the Redis connection pool.
        Should be called during application startup.
        """
        if self._pool is None:
            logger.info(f"Initializing Redis connection pool to {self._redis_url}")
            self._pool = redis.asyncio.ConnectionPool.from_url(
                self._redis_url,
                max_connections=self._max_connections,
                decode_responses=True,  ***REMOVED*** Auto-decode bytes to strings
            )

    @critical_service_handler("redis", logger)
    async def shutdown(self) -> None:
        """
        Close the Redis connection pool.
        Should be called during application shutdown.
        """
        if self._pool is not None:
            logger.info("Closing Redis connection pool")
            await self._pool.disconnect()
            self._pool = None

    @optional_service_handler(service_name="redis", logger=logger, fallback_value=[])
    async def get_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on the provided query prefix.

        This implementation provides two approaches:
        1. Using ZRANGE with lexicographical ordering (Redis 6.2+)
        2. Using KEYS or SCAN with pattern matching as a fallback

        Args:
            query: The search query prefix
            limit: Maximum number of suggestions to return

        Returns:
            A list of suggestion strings matching the prefix (empty list if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty list if Redis is unavailable
            instead of failing the search completely.
        """
        if not query:
            return []

        if self._pool is None:
            logger.warning("Redis pool not initialized, initializing now")
            await self.initialize()

        query_prefix = query.lower().strip()

        async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
            ***REMOVED*** First try exact match to catch known titles
            exact_key = f"{self._suggestion_key_prefix}{query_prefix}"
            exists = await redis_client.exists(exact_key)
            if exists:
                ***REMOVED*** If exact match exists, prioritize it
                suggestions = [query_prefix]
                ***REMOVED*** But still get other matches to fill up to limit
                return suggestions + await self._get_prefix_matches(
                    redis_client, query_prefix, limit - len(suggestions)
                )

            ***REMOVED*** If no exact match, try prefix matching
            return await self._get_prefix_matches(redis_client, query_prefix, limit)

    async def _get_prefix_matches(
        self, redis_client: Any, query_prefix: str, limit: int
    ) -> List[str]:
        """
        Get suggestions that match the given prefix using various strategies.

        Args:
            redis_client: Redis client instance
            query_prefix: The prefix to search for
            limit: Maximum number of results to return

        Returns:
            List of matching suggestion strings
        """
        ***REMOVED*** Method 1: Use sorted set with lexicographical range
        try:
            ***REMOVED*** Get suggestions using lexicographical range query (Redis 6.2+)
            ***REMOVED*** Implementation depends on Redis version:
            try:
                ***REMOVED*** Redis 6.2+ method - Using simplified approach for type safety
                suggestions = await redis_client.zrange(
                    "suggestions",
                    0,  ***REMOVED*** Start index (simplified)
                    -1,  ***REMOVED*** End index (simplified)
                )
                ***REMOVED*** Filter the results manually since we can't use the params directly
                filtered_suggestions = [
                    s for s in suggestions if isinstance(s, str) and s.startswith(query_prefix)
                ]
                if filtered_suggestions:
                    return filtered_suggestions[:limit]
            except Exception:
                ***REMOVED*** Older Redis versions fallback
                logger.warning("Falling back to older Redis zrangebylex method")
                suggestions = await redis_client.execute_command(
                    "ZRANGEBYLEX",
                    "suggestions",
                    f"[{query_prefix}",
                    f"[{query_prefix}\xff",
                    "LIMIT",
                    "0",
                    str(limit),
                )
                ***REMOVED*** Convert bytes to strings if needed
                if suggestions and isinstance(suggestions[0], bytes):
                    suggestions = [s.decode("utf-8") for s in suggestions]
                if suggestions:
                    return cast(List[str], suggestions[:limit])
        except Exception as e:
            logger.warning(f"Error using sorted set method: {str(e)}")

        ***REMOVED*** Method 2: Use keys with pattern matching as fallback
        ***REMOVED*** This is less efficient but more compatible
        pattern = f"{self._suggestion_key_prefix}{query_prefix}*"

        ***REMOVED*** Try KEYS command for small datasets
        try:
            keys = await redis_client.keys(pattern)
            ***REMOVED*** Extract suggestions from keys (format: suggestions:<suggestion>)
            suggestions = []
            for key in keys:
                if ":" in key:
                    parts = key.split(":", 1)
                    if len(parts) > 1:
                        suggestions.append(parts[1])
                        if len(suggestions) >= limit:
                            break
            return cast(List[str], suggestions)
        except Exception as e:
            logger.warning(f"Error using KEYS: {str(e)}")

        ***REMOVED*** Method 3: Use SCAN as final fallback (most compatible but slowest)
        try:
            cursor = 0
            suggestions = []

            scan_complete = False
            while len(suggestions) < limit and not scan_complete:
                cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
                ***REMOVED*** Extract suggestions from keys
                for key in keys:
                    if ":" in key:
                        parts = key.split(":", 1)
                        if len(parts) > 1:
                            suggestions.append(parts[1])
                            if len(suggestions) >= limit:
                                break

                ***REMOVED*** Check if we've scanned all keys
                if cursor == 0:
                    scan_complete = True

            ***REMOVED*** If we still don't have any matches, try a more flexible approach
            if not suggestions and len(query_prefix) > 2:
                ***REMOVED*** Try with * wildcard for more flexible matching
                pattern = f"{self._suggestion_key_prefix}*{query_prefix}*"
                cursor = 0

                while len(suggestions) < limit:
                    cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
                    ***REMOVED*** Extract suggestions from keys
                    for key in keys:
                        ***REMOVED*** Process key properly based on its type
                        key_str = key if isinstance(key, str) else key.decode("utf-8")

                        if ":" in key_str:
                            parts = key_str.split(":", 1)
                            if len(parts) > 1 and parts[1] not in suggestions:
                                suggestions.append(parts[1])
                                if len(suggestions) >= limit:
                                    break

                    ***REMOVED*** Break if we've scanned all keys
                    if cursor == 0:
                        break

            return cast(List[str], suggestions[:limit])
        except Exception as e:
            logger.error(f"All Redis suggestion methods failed: {str(e)}")
            return []

    async def _get_substring_matches(
        self, redis_client: Any, query_prefix: str, limit: int
    ) -> List[str]:
        """
        Get suggestions that contain the query as a substring.

        This method performs substring matching by scanning entity keys
        for entries that contain the query string anywhere in their name.

        Args:
            redis_client: Redis client instance
            query_prefix: The substring to search for
            limit: Maximum number of results to return

        Returns:
            List of matching suggestion strings
        """
        if not query_prefix or limit <= 0:
            return []

        matches: List[str] = []
        start_time = time.time()

        try:
            ***REMOVED*** Search through entity keys to find titles/names containing the query substring
            ***REMOVED*** Look for movies, actors, and directors containing the substring
            entity_patterns = [
                f"{self._entity_key_prefix}{e_type}:*{query_prefix}*"
                for e_type in self._entity_types
            ]

            for pattern in entity_patterns:
                ***REMOVED*** Use SCAN for better performance and scalability
                cursor = 0
                while len(matches) < limit:
                    cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
                    for key in keys:
                        ***REMOVED*** Process key properly based on its type
                        key_str = key if isinstance(key, str) else key.decode("utf-8")

                        ***REMOVED*** Extract the entity name from the key (everything after "entity:type:")
                        if key_str.startswith(self._entity_key_prefix):
                            ***REMOVED*** Split: entity:movie:napoleon -> ["entity", "movie", "napoleon"]
                            parts = key_str.split(":", 2)
                            if len(parts) >= 3:
                                entity_name = parts[2]  ***REMOVED*** "napoleon"
                                ***REMOVED*** Only add non-empty entity names that aren't duplicates
                                if entity_name and entity_name not in matches:
                                    matches.append(entity_name)

                                    if len(matches) >= limit:
                                        break

                    ***REMOVED*** Break if we've scanned all keys
                    if cursor == 0:
                        break

                if len(matches) >= limit:
                    break

        except Exception as e:
            logger.warning(f"Error in substring matching: {str(e)}")

        finally:
            duration = time.time() - start_time
            if duration > 0.1:  ***REMOVED*** Log slow queries (>100ms)
                logger.warning(
                    f"Slow substring search: '{query_prefix}' took {duration:.3f}s, found {len(matches)} matches"
                )
            elif duration > 0.05:  ***REMOVED*** Debug log for moderately slow queries (>50ms)
                logger.debug(
                    f"Substring search: '{query_prefix}' took {duration:.3f}s, found {len(matches)} matches"
                )

        return matches

    @optional_service_handler(service_name="redis", logger=logger, fallback_value=[])
    async def get_entity_suggestions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get enhanced entity-based suggestions (movies, actors, directors) with detailed information.

        Args:
            query: The search query prefix
            limit: Maximum number of suggestions to return

        Returns:
            A list of suggestion objects with entity details (empty list if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty list if Redis is unavailable
            instead of failing the search completely.
        """
        if not query:
            return []

        if self._pool is None:
            logger.warning("Redis pool not initialized, initializing now")
            await self.initialize()

        query_prefix = query.lower().strip()

        async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
            ***REMOVED*** First try with the query as is
            suggestions = await self.get_suggestions(query_prefix, limit)

            ***REMOVED*** If we didn't get enough results, try more aggressive matching
            if len(suggestions) < min(3, limit) and len(query_prefix) >= 3:
                ***REMOVED*** Try again using just the first part of the query if it has spaces
                if " " in query_prefix:
                    first_word = query_prefix.split()[0]
                    if len(first_word) >= 3:
                        more_suggestions = await self.get_suggestions(
                            first_word, limit - len(suggestions)
                        )
                        ***REMOVED*** Add suggestions that aren't already included
                        for sugg in more_suggestions:
                            if sugg not in suggestions:
                                suggestions.append(sugg)
                                if len(suggestions) >= limit:
                                    break

            ***REMOVED*** Smart substring matching: always try for 3+ char queries to enhance results
            if len(query_prefix) >= 3 and len(suggestions) < limit:
                ***REMOVED*** Calculate how many more results we need
                remaining_slots = limit - len(suggestions)

                ***REMOVED*** For insufficient results, be more aggressive with substring matching
                if len(suggestions) < min(3, limit):
                    substring_limit = min(8, max(3, remaining_slots + 3))
                else:
                    ***REMOVED*** For good results, just add a few substring matches for enhancement
                    substring_limit = min(5, max(2, remaining_slots + 2))

                substring_suggestions = await self._get_substring_matches(
                    redis_client, query_prefix, substring_limit
                )

                ***REMOVED*** Add substring matches that aren't already included
                for sugg in substring_suggestions:
                    if sugg not in suggestions:
                        suggestions.append(sugg)
                        if len(suggestions) >= limit:
                            break

            ***REMOVED*** Convert suggestions to detailed entity objects
            detailed_suggestions = []
            seen_ids: set[int] = set()  ***REMOVED*** Track seen entity IDs to prevent duplicates

            for suggestion in suggestions:
                ***REMOVED*** Look for a detailed entity record in Redis
                ***REMOVED*** First try to get the movie ID from the suggestion key
                suggestion_key = f"{self._suggestion_key_prefix}{suggestion}"
                movie_id = await redis_client.get(suggestion_key)

                entity_data = None
                entity_type = None

                if movie_id:
                    ***REMOVED*** Try to find the entity by movie ID using a more efficient approach
                    try:
                        movie_id_int = int(
                            movie_id.decode() if isinstance(movie_id, bytes) else movie_id
                        )

                        ***REMOVED*** Check if we have a direct entity lookup by ID (future enhancement)
                        entity_by_id_key = f"entity:id:{movie_id_int}"
                        id_data_json = await redis_client.get(entity_by_id_key)
                        if id_data_json:
                            try:
                                entity_data = json.loads(id_data_json)
                                entity_type = entity_data.get("type", "movie")
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in Redis for key {entity_by_id_key}")
                    except (ValueError, TypeError):
                        movie_id_str = (
                            movie_id.decode() if isinstance(movie_id, bytes) else str(movie_id)
                        )
                        logger.warning(
                            f"Invalid movie ID in Redis for suggestion {suggestion}: {movie_id_str}"
                        )

                ***REMOVED*** If no entity data found by ID, try direct entity lookup
                if entity_data is None:
                    entity_types = ["movie", "actor", "director"]
                    for e_type in entity_types:
                        entity_key = f"{self._entity_key_prefix}{e_type}:{suggestion}"
                        data_json = await redis_client.get(entity_key)
                        if data_json:
                            try:
                                entity_data = json.loads(data_json)
                                entity_type = e_type
                                break
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in Redis for key {entity_key}")

                ***REMOVED*** If no entity data found, create basic suggestion
                if entity_data is None:
                    movie_id_str = (
                        movie_id.decode()
                        if isinstance(movie_id, bytes)
                        else str(movie_id) if movie_id else "None"
                    )
                    logger.debug(
                        f"No entity data found for suggestion '{suggestion}' (movie_id: {movie_id_str}), using defaults"
                    )
                    entity_data = {
                        "text": suggestion,
                        "type": "movie",  ***REMOVED*** Default to movie
                        "id": (
                            int(movie_id.decode() if isinstance(movie_id, bytes) else movie_id)
                            if movie_id
                            else hash(suggestion) % 100000
                        ),
                        ***REMOVED*** Add some basic fields to avoid null values
                        "image_path": None,
                        "year": None,
                        "popularity": 0.0,
                    }
                    entity_type = "movie"

                ***REMOVED*** Enhance entity data with additional fields
                suggestion_obj = {
                    "text": entity_data.get("title", entity_data.get("name", suggestion)),
                    "type": entity_type or entity_data.get("type", "movie"),
                    "id": entity_data.get("id", 0),
                    "image_path": entity_data.get("poster_url")
                    or entity_data.get("image_path")
                    or entity_data.get("profile_path"),
                    "year": entity_data.get("release_year")
                    or entity_data.get("year")
                    or entity_data.get("birth_year"),
                    "popularity": entity_data.get("popularity", 0.0),
                    "additional_info": {
                        key: value
                        for key, value in entity_data.items()
                        if key not in ["text", "type", "id", "image_path", "year", "popularity"]
                    },
                }

                ***REMOVED*** Add image URL processing
                if suggestion_obj["image_path"] and not suggestion_obj["image_path"].startswith(
                    "http"
                ):
                    suggestion_obj["image_path"] = (
                        f"{TMDB_IMAGE_BASE_URL}{suggestion_obj['image_path']}"
                    )

                ***REMOVED*** Check for duplicate IDs before adding
                entity_id = suggestion_obj.get("id")
                if entity_id is not None and entity_id in seen_ids:
                    logger.debug(
                        f"Skipping duplicate entity ID {entity_id} for suggestion '{suggestion}'"
                    )
                    continue

                ***REMOVED*** Track this ID to prevent future duplicates
                if entity_id is not None:
                    seen_ids.add(entity_id)

                detailed_suggestions.append(suggestion_obj)

                if len(detailed_suggestions) >= limit:
                    break

            ***REMOVED*** Sort suggestions by relevance (exact matches first, then by score)
            def sort_key(sugg: Dict[str, Any]) -> Tuple[int, float]:
                ***REMOVED*** Exact matches should be prioritized
                if sugg["text"] == query_prefix:
                    return (0, sugg.get("popularity", 0) or 0)
                ***REMOVED*** Then prioritize by how closely the text starts with the query
                elif sugg["text"].startswith(query_prefix):
                    return (1, sugg.get("popularity", 0) or 0)
                ***REMOVED*** Then suggestions where the query is a word in the text
                elif f" {query_prefix}" in f" {sugg['text']} ":
                    return (2, sugg.get("popularity", 0) or 0)
                ***REMOVED*** Finally by default popularity/score
                else:
                    return (3, sugg.get("popularity", 0) or 0)

            detailed_suggestions.sort(key=sort_key, reverse=True)

            return detailed_suggestions[:limit]

    @optional_service_handler(service_name="redis", logger=logger, fallback_value=[])
    async def get_ranked_suggestions(
        self,
        query: str,
        limit: int = 10,
        fallback_to_fuzzy: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get ranked suggestions with advanced scoring and fuzzy matching fallback.

        Args:
            query: The search query
            limit: Maximum number of suggestions to return
            fallback_to_fuzzy: Whether to use fuzzy matching if no exact matches

        Returns:
            A list of ranked suggestion objects (empty list if Redis unavailable)

        Note:
            Uses graceful degradation - returns empty list if Redis is unavailable
        """
        if not query:
            return []

        ***REMOVED*** Start with entity suggestions
        suggestions = await self.get_entity_suggestions(query, limit)

        ***REMOVED*** If we don't have enough results and fuzzy matching is enabled
        if len(suggestions) < limit and fallback_to_fuzzy and len(query) >= 3:
            ***REMOVED*** Try partial word matching
            words = query.lower().split()
            if words:
                for word in words:
                    if len(word) >= 3:
                        fuzzy_suggestions = await self.get_entity_suggestions(
                            word, limit - len(suggestions)
                        )
                        ***REMOVED*** Add unique suggestions
                        existing_texts = {s["text"].lower() for s in suggestions}
                        for sugg in fuzzy_suggestions:
                            if sugg["text"].lower() not in existing_texts:
                                ***REMOVED*** Mark as partial match
                                sugg["is_partial"] = True
                                sugg["search_type"] = "fuzzy"
                                suggestions.append(sugg)
                                existing_texts.add(sugg["text"].lower())
                                if len(suggestions) >= limit:
                                    break
                        if len(suggestions) >= limit:
                            break

        ***REMOVED*** Enhance suggestions with search metadata
        for i, sugg in enumerate(suggestions):
            if "search_type" not in sugg:
                sugg["search_type"] = (
                    "exact" if sugg["text"].lower().startswith(query.lower()) else "partial"
                )
            if "is_partial" not in sugg:
                sugg["is_partial"] = not sugg["text"].lower().startswith(query.lower())

        return suggestions[:limit]

    @optional_service_handler(
        service_name="redis",
        logger=logger,
        fallback_value={"status": "unhealthy", "error": "Redis connection failed"},
    )
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Redis connection.

        Returns:
            Dictionary containing health status, Redis URL, and any error details
        """
        try:
            if self._pool is None:
                return {
                    "status": "unhealthy",
                    "error": "Redis connection pool not initialized",
                    "redis_url": self._redis_url,
                }

            ***REMOVED*** Test the connection by performing a simple operation
            redis_client = redis.asyncio.Redis(connection_pool=self._pool)

            ***REMOVED*** Simple ping to test connectivity
            await redis_client.ping()

            ***REMOVED*** Get some basic info
            info = await redis_client.info()
            redis_version = info.get("redis_version", "unknown")

            return {
                "status": "healthy",
                "redis_url": self._redis_url,
                "redis_version": redis_version,
                "max_connections": self._max_connections,
                "features": {
                    "prefix_matching": True,
                    "entity_lookup": True,
                    "fuzzy_matching": True,
                    "suggestion_caching": True,
                },
            }

        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "redis_url": self._redis_url,
            }

    @staticmethod
    def format_suggestions(raw_suggestions: List[str]) -> List[Dict[str, Any]]:
        """
        Format raw suggestion strings into structured suggestion objects.

        This is useful if you want to add metadata to each suggestion.
        If your Redis already stores formatted suggestions, you can skip this.

        Args:
            raw_suggestions: List of raw suggestion strings from Redis

        Returns:
            List of structured suggestion objects
        """
        return [{"text": suggestion, "score": 1.0} for suggestion in raw_suggestions]
