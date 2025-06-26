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
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, cast

import redis.asyncio
from redis.exceptions import RedisError

from config.logging import get_logger

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

    def __init__(self, redis_url: str, pool_size: int = 10):
        """
        Initialize the suggestion engine with Redis connection parameters.

        Args:
            redis_url: Redis connection URL in format redis://host:port/db
            pool_size: Size of the Redis connection pool
        """
        self._redis_url = redis_url
        self._pool: Optional[redis.asyncio.ConnectionPool] = None  ***REMOVED*** type: ignore
        self._pool_size = pool_size

    async def initialize(self) -> None:
        """
        Initialize the Redis connection pool.
        Should be called during application startup.
        """
        if self._pool is None:
            logger.info(f"Initializing Redis connection pool to {self._redis_url}")
            self._pool = redis.asyncio.ConnectionPool.from_url(
                self._redis_url,
                max_connections=self._pool_size,
                decode_responses=True,  ***REMOVED*** Auto-decode bytes to strings
            )

    async def shutdown(self) -> None:
        """
        Close the Redis connection pool.
        Should be called during application shutdown.
        """
        if self._pool is not None:
            logger.info("Closing Redis connection pool")
            await self._pool.disconnect()
            self._pool = None

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
            A list of suggestion strings matching the prefix

        Raises:
            RedisError: If there was an issue communicating with Redis
        """
        if not query:
            return []

        if self._pool is None:
            logger.warning("Redis pool not initialized, initializing now")
            await self.initialize()

        query_prefix = query.lower().strip()

        try:
            async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
                ***REMOVED*** First try exact match to catch known titles
                exact_key = f"suggestions:{query_prefix}"
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

        except RedisError as e:
            logger.error(f"Redis error while getting suggestions: {str(e)}")
            raise

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
        pattern = f"suggestions:{query_prefix}*"

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
                pattern = f"suggestions:*{query_prefix}*"
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

    async def get_entity_suggestions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get enhanced entity-based suggestions (movies, actors, directors) with detailed information.

        Args:
            query: The search query prefix
            limit: Maximum number of suggestions to return

        Returns:
            A list of suggestion objects with entity details

        Raises:
            RedisError: If there was an issue communicating with Redis
        """
        if not query:
            return []

        if self._pool is None:
            logger.warning("Redis pool not initialized, initializing now")
            await self.initialize()

        query_prefix = query.lower().strip()

        try:
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

                    ***REMOVED*** If the query might be a word prefix, try a more aggressive matching approach
                    if len(suggestions) < min(5, limit):
                        ***REMOVED*** Try with prefix wildcard matching for shorter queries
                        pattern = f"suggestions:*{query_prefix}*"
                        keys = await redis_client.keys(pattern)
                        for key in keys:
                            ***REMOVED*** Process key properly based on its type
                            key_str = key.decode("utf-8") if isinstance(key, bytes) else key

                            if ":" in key_str:
                                parts = key_str.split(":", 1)
                                if len(parts) > 1 and parts[1] not in suggestions:
                                    suggestions.append(parts[1])
                                    if len(suggestions) >= limit:
                                        break

                ***REMOVED*** For each suggestion, try to get detailed entity information
                detailed_suggestions = []

                for suggestion in suggestions:
                    ***REMOVED*** Look for a detailed entity record in Redis
                    ***REMOVED*** Format: entity:type:name (e.g. entity:movie:inception)
                    entity_types = ["movie", "actor", "director"]
                    entity_data = None
                    entity_type = None

                    for e_type in entity_types:
                        entity_key = f"entity:{e_type}:{suggestion}"
                        data_json = await redis_client.get(entity_key)
                        if data_json:
                            try:
                                entity_data = json.loads(data_json)
                                entity_type = e_type
                                break
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in Redis for key {entity_key}")

                    if entity_data and entity_type:
                        ***REMOVED*** Build a rich suggestion with entity data

                        ***REMOVED*** Process image path to ensure it has base URL
                        image_path = entity_data.get("image_path")
                        if image_path and image_path.startswith("/"):
                            ***REMOVED*** Add TMDB base URL to image path
                            image_path = f"{TMDB_IMAGE_BASE_URL}{image_path}"

                        detailed_suggestion = {
                            "text": suggestion,
                            "type": entity_type,
                            "id": entity_data.get("id"),
                            "image_path": image_path,
                            "year": entity_data.get("year"),
                            "popularity": entity_data.get("popularity"),
                            "additional_info": {
                                k: v
                                for k, v in entity_data.items()
                                if k not in ["id", "image_path", "year", "popularity"]
                            },
                        }
                    else:
                        ***REMOVED*** Fallback to basic suggestion if no entity data found
                        detailed_suggestion = {
                            "text": suggestion,
                            "type": "unknown",
                        }

                    detailed_suggestions.append(detailed_suggestion)

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

        except RedisError as e:
            logger.error(f"Redis error while getting entity suggestions: {str(e)}")
            raise

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

    async def get_ranked_suggestions(
        self, query: str, limit: int = 10, fallback_to_fuzzy: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced and ranked search suggestions with deduplication and scoring.

        This method improves upon the basic get_entity_suggestions by:
        - Deduplicating results by entity ID
        - Normalizing text for better matching
        - Filtering out low-quality unknown entries
        - Scoring and ranking results
        - Adding metadata for UI rendering

        Args:
            query: The search query prefix
            limit: Maximum number of suggestions to return
            fallback_to_fuzzy: Whether to try fuzzy matching if exact prefix fails

        Returns:
            A list of high-quality, deduplicated, and ranked suggestion objects
        """
        if not query:
            return []

        query_prefix = query.lower().strip()

        ***REMOVED*** Get raw suggestions with increased limit to account for duplicates we'll remove
        raw_suggestions = await self.get_entity_suggestions(query_prefix, limit * 3)

        ***REMOVED*** Create a mapping to deduplicate by ID while keeping the best match for each entity
        entity_map = {}  ***REMOVED*** ID -> best suggestion
        matched_ids = defaultdict(list)  ***REMOVED*** ID -> list of matches (to find best)

        ***REMOVED*** First pass: Group by ID and collect all matches
        for suggestion in raw_suggestions:
            entity_id = suggestion.get("id")
            entity_type = suggestion.get("type")

            ***REMOVED*** Skip items without an ID unless they're our last resort
            if entity_id is None and entity_type == "unknown":
                continue

            ***REMOVED*** If this is a new ID or a better match for existing ID, store it
            if entity_id is not None:
                matched_ids[entity_id].append(suggestion)

        ***REMOVED*** Second pass: For each ID, select the best suggestion
        for entity_id, matches in matched_ids.items():
            ***REMOVED*** Skip if no valid matches
            if not matches:
                continue

            ***REMOVED*** Score function to determine the best match for an entity
            def get_match_score(match: Dict[str, Any]) -> float:
                ***REMOVED*** Base score is 0
                score = 0
                text = match.get("text", "").lower()

                ***REMOVED*** Prioritize exact matches with the query
                if text == query_prefix:
                    score += 1000
                ***REMOVED*** Then matches that start with query
                elif text.startswith(query_prefix):
                    score += 500
                ***REMOVED*** Then matches containing the query as a word
                elif f" {query_prefix}" in f" {text} ":
                    score += 200
                ***REMOVED*** Finally matches containing the query anywhere
                elif query_prefix in text:
                    score += 100

                ***REMOVED*** Adjust score by entity type
                type_scores = {"movie": 10, "actor": 8, "director": 6, "unknown": 0}
                score += type_scores.get(match.get("type", "unknown"), 0)

                ***REMOVED*** Boost by popularity
                popularity = match.get("popularity") or 0
                if popularity:
                    score += min(popularity, 20)  ***REMOVED*** Cap popularity impact

                return score

            ***REMOVED*** Get the best match for this entity
            best_match = max(matches, key=get_match_score)
            entity_map[entity_id] = best_match

        ***REMOVED*** Prepare final suggestions
        final_suggestions = list(entity_map.values())

        ***REMOVED*** Calculate composite score for ranking
        for suggestion in final_suggestions:
            ***REMOVED*** Create a composite score using vote_average and popularity
            vote_avg = suggestion.get("additional_info", {}).get("vote_average", 0) or 0
            popularity = suggestion.get("popularity", 0) or 0

            ***REMOVED*** Basic composite score formula
            composite_score: float = 0
            if vote_avg and popularity:
                ***REMOVED*** This formula prioritizes highly rated popular content
                composite_score = vote_avg * math.log1p(popularity)
            elif vote_avg:
                composite_score = vote_avg
            elif popularity:
                composite_score = math.log1p(popularity)

            suggestion["composite_score"] = composite_score

            ***REMOVED*** Add flags for client-side rendering
            entity_type = suggestion.get("type")
            suggestion["is_partial"] = entity_type == "unknown" or not suggestion.get("id")

            ***REMOVED*** Determine search_type - how this result was matched
            text = suggestion.get("text", "").lower()
            if text == query_prefix:
                suggestion["search_type"] = "exact"
            elif text.startswith(query_prefix):
                suggestion["search_type"] = "prefix"
            elif f" {query_prefix}" in f" {text} ":
                suggestion["search_type"] = "word"
            else:
                suggestion["search_type"] = "contains"

            ***REMOVED*** Normalize and enhance additional_info
            if "additional_info" not in suggestion:
                suggestion["additional_info"] = {}

            ***REMOVED*** Set proper title in additional_info if available
            if entity_type == "movie" and "title" not in suggestion["additional_info"]:
                suggestion["additional_info"]["title"] = suggestion.get("text", "").title()

        ***REMOVED*** Sort by composite score (descending)
        final_suggestions.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

        ***REMOVED*** If we don't have enough good suggestions and fallback is enabled, try fuzzy matching
        if fallback_to_fuzzy and len(final_suggestions) < min(limit, 3) and len(query_prefix) >= 3:
            ***REMOVED*** We'd implement fuzzy matching here, but for now we'll just use our
            ***REMOVED*** existing suggestion engine with modified parameters
            pass

        ***REMOVED*** Ensure we only return the requested limit
        final_suggestions = final_suggestions[:limit]

        ***REMOVED*** Remove the temporary composite_score from the output
        for suggestion in final_suggestions:
            suggestion.pop("composite_score", None)

        return final_suggestions

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Redis connection and suggestion engine.

        Returns:
            Health status information
        """
        try:
            if self._pool is None:
                return {
                    "status": "unhealthy",
                    "error": "Redis pool not initialized",
                    "redis_url": (
                        self._redis_url.split("@")[-1]
                        if "@" in self._redis_url
                        else self._redis_url
                    ),
                }

            async with redis.asyncio.Redis(connection_pool=self._pool) as redis_client:
                ***REMOVED*** Test basic connectivity
                pong = await redis_client.ping()
                if not pong:
                    return {
                        "status": "unhealthy",
                        "error": "Redis ping failed",
                        "redis_url": (
                            self._redis_url.split("@")[-1]
                            if "@" in self._redis_url
                            else self._redis_url
                        ),
                    }

                ***REMOVED*** Test suggestion functionality
                test_suggestions = await self.get_suggestions("test", 1)

                return {
                    "status": "healthy",
                    "redis_url": (
                        self._redis_url.split("@")[-1]
                        if "@" in self._redis_url
                        else self._redis_url
                    ),
                    "pool_size": self._pool_size,
                    "test_suggestions_count": len(test_suggestions),
                    "features": {
                        "basic_suggestions": True,
                        "entity_suggestions": True,
                        "ranked_suggestions": True,
                        "redis_caching": True,
                    },
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "redis_url": (
                    self._redis_url.split("@")[-1] if "@" in self._redis_url else self._redis_url
                ),
            }
