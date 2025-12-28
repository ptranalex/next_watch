"""
Core SuggestionEngine class.

This module contains the main SuggestionEngine class that orchestrates
all the suggestion functionality.
"""

import contextlib
import json
from typing import Any

import redis.asyncio
from config.logging import get_logger
from fast_core.errors import critical_service_handler, optional_service_handler

from .hydration import EntityHydrator
from .matching import MatchingStrategies
from .ranking import SuggestionRanker
from .utils import DEFAULT_ENTITY_TYPES, normalize_query

logger = get_logger(__name__)


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
        entity_types: list[str] | None = None,
        ***REMOVED*** Performance/caching knobs
        suggestion_cache_ttl: int = 900,
        substring_min_length: int = 3,
        substring_time_budget_ms: int = 80,
        substring_scan_page_limit: int = 5,
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
            suggestion_cache_ttl: Cache TTL for suggestions in seconds
            substring_min_length: Minimum length for substring matching
            substring_time_budget_ms: Time budget for substring matching in milliseconds
            substring_scan_page_limit: Maximum pages to scan for substring matching
        """
        self._redis_url = redis_url
        self._pool: redis.asyncio.ConnectionPool | None = None  ***REMOVED*** type: ignore
        self._max_connections = max_connections
        self._suggestion_key_prefix = suggestion_key_prefix
        self._entity_key_prefix = entity_key_prefix
        self._search_result_prefix = search_result_prefix
        self._entity_types = entity_types or DEFAULT_ENTITY_TYPES

        ***REMOVED*** Cache and performance settings
        self._suggestion_cache_ttl = max(0, suggestion_cache_ttl)

        ***REMOVED*** Initialize strategy components
        self._matching = MatchingStrategies(
            suggestion_key_prefix=suggestion_key_prefix,
            entity_key_prefix=entity_key_prefix,
            entity_types=self._entity_types,
            substring_min_length=substring_min_length,
            substring_time_budget_ms=substring_time_budget_ms,
            substring_scan_page_limit=substring_scan_page_limit,
        )

        self._hydrator = EntityHydrator(
            suggestion_key_prefix=suggestion_key_prefix,
            entity_key_prefix=entity_key_prefix,
            entity_types=self._entity_types,
        )

        self._ranker = SuggestionRanker()

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
    async def get_suggestions(self, query: str, limit: int = 10) -> list[str]:
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

        query_prefix = normalize_query(query)

        async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
            ***REMOVED*** First try exact match to catch known titles
            exact_key = f"{self._suggestion_key_prefix}{query_prefix}"
            exists = await redis_client.exists(exact_key)
            if exists:
                ***REMOVED*** If exact match exists, prioritize it
                suggestions = [query_prefix]
                ***REMOVED*** But still get other matches to fill up to limit
                return suggestions + await self._matching.get_prefix_matches(
                    redis_client, query_prefix, limit - len(suggestions)
                )

            ***REMOVED*** If no exact match, try prefix matching
            return await self._matching.get_prefix_matches(redis_client, query_prefix, limit)

    @optional_service_handler(service_name="redis", logger=logger, fallback_value=[])
    async def get_entity_suggestions(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
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

        query_prefix = normalize_query(query)

        async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
            ***REMOVED*** Check cache first
            cache_key = f"cache:suggestions:{query_prefix}:{limit}"
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    try:
                        cached_list = json.loads(cached)
                        if isinstance(cached_list, list):
                            return cached_list[:limit]
                    except json.JSONDecodeError:
                        pass
            except Exception:
                ***REMOVED*** Cache read failures should not break suggestions
                pass

            ***REMOVED*** First try with the query as is
            suggestions = await self.get_suggestions(query_prefix, limit)

            ***REMOVED*** If we didn't get enough results, try more aggressive matching
            if len(suggestions) < min(3, limit) and len(query_prefix) >= 3 and " " in query_prefix:
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

                substring_suggestions = await self._matching.get_substring_matches(
                    redis_client, query_prefix, substring_limit
                )

                ***REMOVED*** Add substring matches that aren't already included
                for sugg in substring_suggestions:
                    if sugg not in suggestions:
                        suggestions.append(sugg)
                        if len(suggestions) >= limit:
                            break

            ***REMOVED*** Convert suggestions to detailed entity objects using batch hydrations
            detailed_suggestions = await self._hydrator.hydrate_suggestions(
                redis_client, suggestions, limit
            )

            ***REMOVED*** Sort suggestions by relevance (exact matches first, then by score)
            detailed_suggestions = self._ranker.sort_suggestions(detailed_suggestions, query_prefix)

            ***REMOVED*** If hydration produced fewer than requested, try to top-up using substring matches
            if len(detailed_suggestions) < limit and len(query_prefix) >= 3:
                needed = limit - len(detailed_suggestions)
                try:
                    extra_candidates = await self._matching.get_substring_matches(
                        redis_client, query_prefix, min(needed + 3, max(needed, 5))
                    )
                except Exception:
                    extra_candidates = []

                if extra_candidates:
                    suggestion_texts_seen = {s["text"] for s in detailed_suggestions}
                    seen_ids: set[int] = {
                        s["id"]
                        for s in detailed_suggestions
                        if s.get("id") is not None and isinstance(s.get("id"), int)
                    }

                    extra_suggestions = await self._hydrator.hydrate_extra_suggestions(
                        redis_client, extra_candidates, suggestion_texts_seen, seen_ids, needed
                    )

                    detailed_suggestions.extend(extra_suggestions)

            final_results = detailed_suggestions[:limit]

            ***REMOVED*** Write-through cache
            if self._suggestion_cache_ttl > 0:
                with contextlib.suppress(Exception):
                    await redis_client.set(
                        cache_key, json.dumps(final_results), ex=self._suggestion_cache_ttl
                    )

            return final_results

    @optional_service_handler(service_name="redis", logger=logger, fallback_value=[])
    async def get_ranked_suggestions(
        self,
        query: str,
        limit: int = 10,
        fallback_to_fuzzy: bool = True,
    ) -> list[dict[str, Any]]:
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
                        suggestions = self._ranker.merge_unique_suggestions(
                            suggestions, fuzzy_suggestions, limit, mark_additional_as_fuzzy=True
                        )
                        if len(suggestions) >= limit:
                            break

        ***REMOVED*** Enhance suggestions with search metadata
        suggestions = self._ranker.enhance_with_search_metadata(suggestions, query)

        return suggestions[:limit]

    @optional_service_handler(
        service_name="redis",
        logger=logger,
        fallback_value={"status": "unhealthy", "error": "Redis connection failed"},
    )
    async def health_check(self) -> dict[str, Any]:
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
