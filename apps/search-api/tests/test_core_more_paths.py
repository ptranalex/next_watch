"""More unit tests to cover SuggestionEngine core paths."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


class _RedisCM:
    def __init__(self, client):
        self._client = client

    async def __aenter__(self):
        return self._client

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_get_entity_suggestions_cache_miss_full_flow(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x", suggestion_cache_ttl=10)
    engine._pool = object()

    redis = AsyncMock()
    redis.get.return_value = None
    redis.exists.return_value = 0
    redis.set.return_value = True

    # avoid real redis
    import redis.asyncio

    monkeypatch.setattr(redis.asyncio, "Redis", lambda connection_pool=None: _RedisCM(redis))

    # Force limited initial suggestions so substring path runs
    async def fake_get_suggestions(q: str, limit: int = 10):
        return ["leo"]

    engine.get_suggestions = fake_get_suggestions  # type: ignore

    engine._matching.get_substring_matches = AsyncMock(return_value=["leon", "leonardo"])  # type: ignore
    engine._hydrator.hydrate_suggestions = AsyncMock(
        return_value=[{"text": "leo", "id": 1, "popularity": 1.0}]
    )
    engine._hydrator.hydrate_extra_suggestions = AsyncMock(
        return_value=[{"text": "leon", "id": 2, "popularity": 0.5}]
    )

    out = await engine.get_entity_suggestions("leo", limit=2)
    assert len(out) == 2

    # write-through cache should be attempted
    assert redis.set.await_count >= 1


@pytest.mark.asyncio
async def test_get_ranked_suggestions_fuzzy_path(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")

    # First call returns 1, second call returns 1 more
    async def fake_entity(q: str, limit: int = 10):
        if q == "star wars":
            return [{"text": "star wars", "id": 1}]
        return [{"text": q, "id": 2}]

    engine.get_entity_suggestions = fake_entity  # type: ignore

    out = await engine.get_ranked_suggestions("star wars", limit=2, fallback_to_fuzzy=True)
    assert len(out) == 2
    assert all("search_type" in s for s in out)


@pytest.mark.asyncio
async def test_health_check_pool_none() -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")
    engine._pool = None

    res = await engine.health_check()
    assert res["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_health_check_happy_path(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")
    engine._pool = object()

    class FakeRedis:
        def __init__(self, connection_pool=None):
            pass

        async def ping(self):
            return True

        async def info(self):
            return {"redis_version": "7.0"}

    import redis.asyncio

    monkeypatch.setattr(redis.asyncio, "Redis", FakeRedis)

    res = await engine.health_check()
    assert res["status"] == "healthy"
    assert res["redis_version"] == "7.0"


@pytest.mark.asyncio
async def test_health_check_exception_path(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")
    engine._pool = object()

    class FakeRedis:
        def __init__(self, connection_pool=None):
            pass

        async def ping(self):
            raise RuntimeError("no")

        async def info(self):
            return {}

    import redis.asyncio

    monkeypatch.setattr(redis.asyncio, "Redis", FakeRedis)

    res = await engine.health_check()
    assert res["status"] == "unhealthy"
    assert "no" in res["error"]
