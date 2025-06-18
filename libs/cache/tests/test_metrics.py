***REMOVED*** type: ignore

"""Tests for cache metrics functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from cache.decorators import redis_cache
from cache.metrics import get_global_collector, set_metrics_enabled
from cache.metrics.storage import reset_global_storage


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test."""
    ***REMOVED*** Reset global storage and collector
    reset_global_storage()

    ***REMOVED*** Also reset the global collector instance
    from cache.metrics.collector import _global_collector
    import cache.metrics.collector as collector_module

    collector_module._global_collector = None

    set_metrics_enabled(True)
    yield

    ***REMOVED*** Clean up after test
    reset_global_storage()
    collector_module._global_collector = None


@pytest.mark.asyncio
async def test_metrics_collection_cache_hit():
    """Test that cache hits are properly recorded."""
    ***REMOVED*** Mock cache manager to simulate cache hit
    with patch("cache.manager.CacheManager.from_settings") as mock_manager_factory:
        mock_manager = AsyncMock()
        mock_manager.get_json.return_value = {"result": "cached_data"}
        mock_manager_factory.return_value = mock_manager

        @redis_cache(ttl=300, key_prefix="test")
        async def test_function(param: str) -> dict:
            return {"result": "fresh_data"}

        ***REMOVED*** Call function - should hit cache
        result = await test_function("test_param")

        ***REMOVED*** Verify result
        assert result == {"result": "cached_data"}

        ***REMOVED*** Check metrics
        collector = get_global_collector()
        metrics = collector.get_metrics()

        assert metrics is not None
        assert metrics["overall"]["total_calls"] == 1
        assert metrics["overall"]["total_hits"] == 1
        assert metrics["overall"]["total_misses"] == 0
        assert metrics["overall"]["hit_ratio"] == 100.0


@pytest.mark.asyncio
async def test_metrics_collection_cache_miss():
    """Test that cache misses are properly recorded."""
    ***REMOVED*** Mock cache manager to simulate cache miss
    with patch("cache.manager.CacheManager.from_settings") as mock_manager_factory:
        mock_manager = AsyncMock()
        mock_manager.get_json.return_value = None  ***REMOVED*** Cache miss
        mock_manager_factory.return_value = mock_manager

        @redis_cache(ttl=300, key_prefix="test")
        async def test_function(param: str) -> dict:
            return {"result": "fresh_data"}

        ***REMOVED*** Call function - should miss cache
        result = await test_function("test_param")

        ***REMOVED*** Verify result
        assert result == {"result": "fresh_data"}

        ***REMOVED*** Check metrics
        collector = get_global_collector()
        metrics = collector.get_metrics()

        assert metrics is not None
        assert metrics["overall"]["total_calls"] == 1
        assert metrics["overall"]["total_hits"] == 0
        assert metrics["overall"]["total_misses"] == 1
        assert metrics["overall"]["miss_ratio"] == 100.0


@pytest.mark.asyncio
async def test_metrics_multiple_functions():
    """Test metrics collection across multiple functions."""
    with patch("cache.manager.CacheManager.from_settings") as mock_manager_factory:
        mock_manager = AsyncMock()
        ***REMOVED*** First call misses, second call hits
        mock_manager.get_json.side_effect = [None, {"result": "cached_data"}]
        mock_manager_factory.return_value = mock_manager

        @redis_cache(ttl=300, key_prefix="func1")
        async def function_one(param: str) -> dict:
            return {"result": "fresh_data_1"}

        @redis_cache(ttl=300, key_prefix="func2")
        async def function_two(param: str) -> dict:
            return {"result": "fresh_data_2"}

        ***REMOVED*** Call functions
        await function_one("param1")  ***REMOVED*** Cache miss
        await function_two("param2")  ***REMOVED*** Cache hit

        ***REMOVED*** Check overall metrics
        collector = get_global_collector()
        metrics = collector.get_metrics()

        assert metrics is not None
        assert metrics["overall"]["total_calls"] == 2
        assert metrics["overall"]["total_hits"] == 1
        assert metrics["overall"]["total_misses"] == 1
        assert metrics["overall"]["hit_ratio"] == 50.0

        ***REMOVED*** Check function-specific metrics
        functions = metrics["functions"]
        assert len(functions) == 2

        ***REMOVED*** Find function metrics (names include module path)
        func1_metrics = None
        func2_metrics = None
        for func_name, func_data in functions.items():
            if "function_one" in func_name:
                func1_metrics = func_data
            elif "function_two" in func_name:
                func2_metrics = func_data

        assert func1_metrics is not None
        assert func1_metrics["hits"] == 0
        assert func1_metrics["misses"] == 1

        assert func2_metrics is not None
        assert func2_metrics["hits"] == 1
        assert func2_metrics["misses"] == 0


@pytest.mark.asyncio
async def test_metrics_disabled():
    """Test that metrics can be disabled."""
    set_metrics_enabled(False)

    with patch("cache.manager.CacheManager.from_settings") as mock_manager_factory:
        mock_manager = AsyncMock()
        mock_manager.get_json.return_value = None
        mock_manager_factory.return_value = mock_manager

        @redis_cache(ttl=300, key_prefix="test", enable_metrics=False)
        async def test_function(param: str) -> dict:
            return {"result": "fresh_data"}

        ***REMOVED*** Call function
        await test_function("test_param")

        ***REMOVED*** Check that no metrics were collected
        collector = get_global_collector()
        metrics = collector.get_metrics()

        ***REMOVED*** Should have no metrics since collection was disabled
        assert metrics is None or metrics["overall"]["total_calls"] == 0


def test_metrics_storage_thread_safety():
    """Test that metrics storage is thread-safe."""
    from cache.metrics.storage import MetricsStorage
    import threading
    import time

    storage = MetricsStorage()

    def record_hits():
        for i in range(100):
            storage.record_hit("test_function", 10.0)
            time.sleep(0.001)  ***REMOVED*** Small delay to increase chance of race conditions

    def record_misses():
        for i in range(100):
            storage.record_miss("test_function", 50.0)
            time.sleep(0.001)

    ***REMOVED*** Run concurrent operations
    thread1 = threading.Thread(target=record_hits)
    thread2 = threading.Thread(target=record_misses)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    ***REMOVED*** Verify final counts
    metrics = storage.get_metrics()
    assert metrics.total_calls == 200
    assert metrics.total_hits == 100
    assert metrics.total_misses == 100


def test_performance_improvement_calculation():
    """Test performance improvement calculation."""
    from cache.metrics.types import FunctionMetrics

    metrics = FunctionMetrics("test_function")

    ***REMOVED*** Record some hits and misses with different times
    metrics.hits = 10
    metrics.total_cache_time_ms = 50.0  ***REMOVED*** 5ms average
    metrics.misses = 5
    metrics.total_uncached_time_ms = 250.0  ***REMOVED*** 50ms average

    assert metrics.avg_cache_time_ms == 5.0
    assert metrics.avg_uncached_time_ms == 50.0
    assert metrics.performance_improvement == 10.0  ***REMOVED*** 50ms / 5ms = 10x improvement
