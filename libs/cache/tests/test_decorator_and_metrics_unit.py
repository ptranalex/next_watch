"""Unit tests for redis_cache decorator and metrics helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_redis_cache_decorator_cache_hit_and_miss(monkeypatch) -> None:
    from cache.decorators.redis_cache import redis_cache

    # fake cache manager
    mgr = AsyncMock()
    mgr.get_json = AsyncMock(side_effect=[{"x": 1}, None])
    mgr.set_json = AsyncMock(return_value=True)

    class FakeCollector:
        def __init__(self):
            self.hits = 0
            self.misses = 0

        def record_cache_hit(self, function_name: str, response_time_ms: float) -> None:
            self.hits += 1

        def record_cache_miss(self, function_name: str, response_time_ms: float) -> None:
            self.misses += 1

    fake_collector = FakeCollector()

    import importlib

    mod = importlib.import_module("cache.decorators.redis_cache")

    monkeypatch.setattr(mod, "get_global_collector", lambda: fake_collector)

    @redis_cache(ttl=10, key_prefix="p", cache_manager=mgr, enable_metrics=True)
    async def f(a: int, b: int = 2):
        return {"a": a, "b": b}

    # hit
    r1 = await f(1)
    assert r1 == {"x": 1}

    # miss
    r2 = await f(3, b=4)
    assert r2 == {"a": 3, "b": 4}
    assert mgr.set_json.await_count >= 1

    assert fake_collector.hits == 1
    assert fake_collector.misses == 1


@pytest.mark.asyncio
async def test_redis_cache_custom_key_builder(monkeypatch) -> None:
    from cache.decorators.redis_cache import redis_cache

    mgr = AsyncMock()
    mgr.get_json = AsyncMock(return_value=None)
    mgr.set_json = AsyncMock(return_value=True)

    @redis_cache(
        ttl=10,
        key_builder=lambda movie_id, user_id=None: f"movie:{movie_id}:user:{user_id or 'anon'}",
        cache_manager=mgr,
        enable_metrics=False,
    )
    async def g(movie_id: int, user_id: int | None = None):
        return {"ok": True}

    await g(1)
    # ensure key_builder path used
    args, kwargs = mgr.get_json.await_args
    assert args[0].startswith("movie:1:user:anon")


def test_metrics_storage_and_collector_smoke() -> None:
    from cache.metrics.collector import MetricsCollector, TimingContext, set_metrics_enabled
    from cache.metrics.storage import get_global_storage, reset_global_storage

    reset_global_storage()
    storage = get_global_storage()
    storage.record_hit("f", 1.0)
    storage.record_miss("f", 2.0)

    fm = storage.get_function_metrics("f")
    assert fm is not None
    assert fm["hits"] == 1

    summary = storage.get_summary()
    assert summary["total_calls"] == 2

    # collector disabled
    c = MetricsCollector(enabled=False)
    assert c.get_metrics() is None

    # timing context records into collector
    set_metrics_enabled(True)
    c2 = MetricsCollector(enabled=True)
    with TimingContext(c2, "x", is_cache_hit=True):
        pass
