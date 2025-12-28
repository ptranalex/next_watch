"""
Matching strategies for search suggestions.

This module contains the core matching logic for prefix and substring searches.
"""

import asyncio
import time
from typing import Any

from config.logging import get_logger

logger = get_logger(__name__)


class MatchingStrategies:
    """
    Collection of matching strategies for search suggestions.
    """

    def __init__(
        self,
        suggestion_key_prefix: str = "suggestions:",
        entity_key_prefix: str = "entity:",
        entity_types: list[str] | None = None,
        substring_min_length: int = 3,
        substring_time_budget_ms: int = 80,
        substring_scan_page_limit: int = 5,
    ):
        """
        Initialize matching strategies.

        Args:
            suggestion_key_prefix: Redis key prefix for suggestions
            entity_key_prefix: Redis key prefix for entities
            entity_types: List of entity types to search
            substring_min_length: Minimum length for substring matching
            substring_time_budget_ms: Time budget for substring matching in milliseconds
            substring_scan_page_limit: Maximum pages to scan for substring matching
        """
        self._suggestion_key_prefix = suggestion_key_prefix
        self._entity_key_prefix = entity_key_prefix
        self._entity_types = entity_types or ["movie", "actor", "director"]
        self._substring_min_length = max(1, substring_min_length)
        self._substring_time_budget_ms = max(10, substring_time_budget_ms)
        self._substring_scan_page_limit = max(1, substring_scan_page_limit)

    async def get_prefix_matches(
        self, redis_client: Any, query_prefix: str, limit: int
    ) -> list[str]:
        """
        Get suggestions that match the given prefix using various strategies.

        Args:
            redis_client: Redis client instance
            query_prefix: The prefix to search for
            limit: Maximum number of results to return

        Returns:
            List of matching suggestion strings
        """
        ***REMOVED*** Method 1: Attempt lexicographical range on zset (primary index)
        try:
            try:
                zlex_suggestions = await redis_client.zrange(
                    "suggestions",
                    f"[{query_prefix}",
                    f"[{query_prefix}\xff",
                    bylex=True,
                    offset=0,
                    num=limit,
                )
                if zlex_suggestions:
                    return list(zlex_suggestions[:limit])
            except Exception:
                ***REMOVED*** Fallback to explicit command for older servers/clients
                logger.warning("Falling back to older Redis ZRANGEBYLEX command")
                zlex_suggestions = await redis_client.execute_command(
                    "ZRANGEBYLEX",
                    "suggestions",
                    f"[{query_prefix}",
                    f"[{query_prefix}\xff",
                    "LIMIT",
                    "0",
                    str(limit),
                )
                if zlex_suggestions and isinstance(zlex_suggestions[0], bytes):
                    zlex_suggestions = [s.decode("utf-8") for s in zlex_suggestions]
                if zlex_suggestions:
                    return list(zlex_suggestions[:limit])
        except Exception as e:
            logger.warning(f"Error using lexicographical range for prefix matches: {str(e)}")

        ***REMOVED*** Method 2: Use SCAN on suggestion keys with a small time budget (fallback)
        try:
            deadline = time.monotonic() + (self._substring_time_budget_ms / 1000.0)
            pattern = f"{self._suggestion_key_prefix}{query_prefix}*"
            cursor = 0
            scan_suggestions: list[str] = []
            pages_scanned = 0

            while len(scan_suggestions) < limit and pages_scanned < self._substring_scan_page_limit:
                if time.monotonic() > deadline:
                    break
                cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=200)
                pages_scanned += 1
                for key in keys:
                    key_str = key if isinstance(key, str) else key.decode("utf-8")
                    if ":" in key_str:
                        parts = key_str.split(":", 1)
                        if len(parts) > 1:
                            value = parts[1]
                            if value not in scan_suggestions:
                                scan_suggestions.append(value)
                                if len(scan_suggestions) >= limit:
                                    break
                if cursor == 0:
                    break

            return list(scan_suggestions[:limit])
        except Exception as e:
            logger.error(f"Prefix SCAN fallback failed: {str(e)}")
            return []

    async def get_substring_matches(
        self, redis_client: Any, query_prefix: str, limit: int
    ) -> list[str]:
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

        matches: list[str] = []
        start_time = time.time()
        deadline = time.monotonic() + (self._substring_time_budget_ms / 1000.0)

        try:
            ***REMOVED*** If query is too short for substring matching, return early
            if len(query_prefix) < self._substring_min_length:
                return []

            async def _scan_entity(pattern: str) -> list[str]:
                results: list[str] = []
                cursor_local = 0
                pages_scanned_local = 0
                while (
                    len(results) < limit and pages_scanned_local < self._substring_scan_page_limit
                ):
                    if time.monotonic() > deadline:
                        break
                    cursor_local, keys_local = await redis_client.scan(
                        cursor=cursor_local, match=pattern, count=200
                    )
                    pages_scanned_local += 1
                    for key_local in keys_local:
                        key_str_local = (
                            key_local if isinstance(key_local, str) else key_local.decode("utf-8")
                        )
                        if key_str_local.startswith(self._entity_key_prefix):
                            parts_local = key_str_local.split(":", 2)
                            if len(parts_local) >= 3:
                                entity_name_local = parts_local[2]
                                if entity_name_local and entity_name_local not in results:
                                    results.append(entity_name_local)
                                    if len(results) >= limit:
                                        break
                    if cursor_local == 0:
                        break
                return results

            patterns = [
                f"{self._entity_key_prefix}{e_type}:*{query_prefix}*"
                for e_type in self._entity_types
            ]
            ***REMOVED*** Run scans concurrently per entity type
            results_per_type = await asyncio.gather(*[_scan_entity(p) for p in patterns])
            ***REMOVED*** Merge results preserving order and uniqueness
            seen: set[str] = set()
            for result_list in results_per_type:
                for name in result_list:
                    if name not in seen:
                        seen.add(name)
                        matches.append(name)
                        if len(matches) >= limit:
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
