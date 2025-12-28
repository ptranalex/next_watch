"""Unit tests for RedisProvider using a fully mocked redis.asyncio client."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


class _FakePool:
    async def disconnect(self):
        return None


class _FakeRedis:
    def __init__(self, **kwargs):
        self._data = {}
        self.get = AsyncMock(side_effect=self._get)
        self.set = AsyncMock(side_effect=self._set)
        self.setex = AsyncMock(side_effect=self._setex)
        self.delete = AsyncMock(side_effect=self._delete)
        self.exists = AsyncMock(side_effect=self._exists)
        self.ping = AsyncMock(return_value=True)
        self.close = AsyncMock(return_value=None)

    async def _get(self, key):
        return self._data.get(key)

    async def _set(self, key, value):
        self._data[key] = value
        return True

    async def _setex(self, key, ttl, value):
        self._data[key] = value
        return True

    async def _delete(self, *keys):
        n = 0
        for k in keys:
            if k in self._data:
                self._data.pop(k, None)
                n += 1
        return n

    async def _exists(self, key):
        return 1 if key in self._data else 0

    async def scan_iter(self, match=None, count=100):
        ***REMOVED*** yield keys matching prefix-style patterns (very simple)
        if match is None:
            return
        prefix = match.rstrip("*")
        for k in list(self._data.keys()):
            if str(k).startswith(prefix):
                yield k


@pytest.mark.asyncio
async def test_redis_provider_core_ops(monkeypatch) -> None:
    from cache.providers import redis as redis_module
    from cache.providers.redis import RedisProvider

    fake_client = _FakeRedis()

    monkeypatch.setattr(redis_module.redis.ConnectionPool, "from_url", lambda *a, **k: _FakePool())
    monkeypatch.setattr(
        redis_module.redis, "Redis", lambda connection_pool=None, decode_responses=True: fake_client
    )

    p = RedisProvider(redis_url="redis://x", key_prefix="t")

    assert await p.set_raw("a", "1") is True
    assert await p.get_raw("a") == "1"
    assert await p.exists("a") is True
    assert await p.delete("a") is True
    assert await p.exists("a") is False

    ***REMOVED*** pattern delete
    await p.set_raw("k:1", "x")
    await p.set_raw("k:2", "y")
    deleted = await p.delete_pattern("k:*")
    assert deleted >= 2

    assert await p.health_check() is True
    await p.close()
