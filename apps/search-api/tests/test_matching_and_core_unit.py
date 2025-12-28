"""Unit tests for Search API suggestion engine matching + core logic."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_matching_prefix_zrange_success() -> None:
    from search_api.services.suggestion_engine.matching import MatchingStrategies

    ms = MatchingStrategies()
    redis = AsyncMock()
    redis.zrange.return_value = ["leo", "leonardo"]

    res = await ms.get_prefix_matches(redis, "leo", 10)
    assert res == ["leo", "leonardo"]


@pytest.mark.asyncio
async def test_matching_prefix_zrangebylex_fallback_decodes_bytes() -> None:
    from search_api.services.suggestion_engine.matching import MatchingStrategies

    ms = MatchingStrategies()
    redis = AsyncMock()
    redis.zrange.side_effect = Exception("no bylex")
    redis.execute_command.return_value = [b"leo", b"leonardo"]

    res = await ms.get_prefix_matches(redis, "leo", 10)
    assert res == ["leo", "leonardo"]


@pytest.mark.asyncio
async def test_matching_prefix_scan_fallback_parses_keys() -> None:
    from search_api.services.suggestion_engine.matching import MatchingStrategies

    ms = MatchingStrategies(substring_scan_page_limit=2)
    redis = AsyncMock()
    redis.zrange.side_effect = Exception("fail")
    redis.execute_command.side_effect = Exception("fail")
    redis.scan.side_effect = [
        (0, ["suggestions:leo", "suggestions:leonardo"]),
    ]

    res = await ms.get_prefix_matches(redis, "leo", 10)
    assert "leo" in res


@pytest.mark.asyncio
async def test_matching_substring_scans_entity_keys() -> None:
    from search_api.services.suggestion_engine.matching import MatchingStrategies

    ms = MatchingStrategies(entity_types=["movie"], substring_scan_page_limit=1)
    redis = AsyncMock()
    redis.scan.return_value = (0, ["entity:movie:napoleon", "entity:movie:leo"])

    res = await ms.get_substring_matches(redis, "leo", 10)
    assert "napoleon" in res
    assert "leo" in res


@pytest.mark.asyncio
async def test_core_get_suggestions_exact_match_path(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")
    engine._pool = object()  ***REMOVED*** prevent initialize

    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 1

    async def fake_prefix(redis_client, query_prefix, limit):
        return ["leonardo"]

    engine._matching.get_prefix_matches = fake_prefix  ***REMOVED*** type: ignore

    class CM:
        async def __aenter__(self):
            return mock_redis

        async def __aexit__(self, exc_type, exc, tb):
            return False

    import redis.asyncio

    monkeypatch.setattr(redis.asyncio, "Redis", lambda connection_pool=None: CM())

    res = await engine.get_suggestions("Leo", limit=5)
    assert res[0] == "leo"  ***REMOVED*** normalized exact


@pytest.mark.asyncio
async def test_core_entity_suggestions_cache_hit(monkeypatch) -> None:
    from search_api.services.suggestion_engine.core import SuggestionEngine

    engine = SuggestionEngine(redis_url="redis://x")
    engine._pool = object()

    cached = json.dumps([{"text": "a"}, {"text": "b"}])

    mock_redis = AsyncMock()
    mock_redis.get.return_value = cached

    class CM:
        async def __aenter__(self):
            return mock_redis

        async def __aexit__(self, exc_type, exc, tb):
            return False

    import redis.asyncio

    monkeypatch.setattr(redis.asyncio, "Redis", lambda connection_pool=None: CM())

    res = await engine.get_entity_suggestions("leo", limit=1)
    assert res == [{"text": "a"}]
