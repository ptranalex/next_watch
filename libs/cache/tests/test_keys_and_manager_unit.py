"""Unit tests for cache key builders and CacheManager helpers."""

from __future__ import annotations

import pytest
from cache.keys.builders import (
    build_cache_key,
    build_filtered_key,
    build_paginated_key,
    hash_parameters,
)
from cache.manager import CacheManager, get_cache_manager
from cache.providers.base import CacheProvider


class DummyProvider(CacheProvider):
    def __init__(self):
        super().__init__(key_prefix="p")
        self._store: dict[str, str] = {}

    async def get_raw(self, key):
        return self._store.get(self._build_key(key))

    async def set_raw(self, key, value, ttl=None):
        self._store[self._build_key(key)] = value
        return True

    async def delete(self, key):
        return self._store.pop(self._build_key(key), None) is not None

    async def exists(self, key):
        return self._build_key(key) in self._store

    async def health_check(self):
        return True

    async def delete_pattern(self, pattern: str) -> int:
        ***REMOVED*** naive pattern delete used only for unit test
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys = [k for k in self._store if k.startswith(prefix)]
            for k in keys:
                self._store.pop(k, None)
            return len(keys)
        return 0


def test_key_builders() -> None:
    assert build_cache_key("movie", ["details", 123, None]) == "nextwatch:movie:details:123"

    h1 = hash_parameters({"a": 1, "b": None})
    h2 = hash_parameters({"a": 1})
    assert h1 == h2

    k = build_filtered_key("genre", 1, {"year": 2023, "rating": 8.5}, user_id=123)
    assert k.startswith("nextwatch:genre:1:filters:")
    assert k.endswith(":user:123")

    kp = build_paginated_key("actor", [123, "movies"], page=2, limit=20, user_id=456)
    assert kp == "nextwatch:actor:123:movies:page:2:limit:20:user:456"


@pytest.mark.asyncio
async def test_cache_manager_safe_helpers_and_singleton() -> None:
    provider = DummyProvider()
    mgr = CacheManager(provider=provider)

    assert await mgr.set_json_safe("k", {"a": 1}) is True
    assert await mgr.get_dict("k") == {"a": 1}
    assert await mgr.get_list("k") is None

    ***REMOVED*** delete pattern supported
    assert await mgr.delete_pattern("p:k*") >= 1

    ***REMOVED*** singleton accessor
    s = get_cache_manager()
    assert s is not None
