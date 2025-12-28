"""Unit tests for suggestion hydration logic."""

from __future__ import annotations

import json

import pytest


class FakePipeline:
    def __init__(self, results, raise_on_execute: bool = False):
        self._results = results
        self._raise = raise_on_execute
        self._gets: list[str] = []

    def get(self, key: str):
        self._gets.append(key)
        return None

    async def execute(self):
        if self._raise:
            raise RuntimeError("pipeline failed")
        return self._results


class FakeRedis:
    def __init__(self, get_map: dict[str, object], pipeline_results=None, raise_pipeline=False):
        self._get_map = get_map
        self._pipeline_results = pipeline_results or []
        self._raise_pipeline = raise_pipeline

    def pipeline(self):
        return FakePipeline(self._pipeline_results, raise_on_execute=self._raise_pipeline)

    async def get(self, key: str):
        return self._get_map.get(key)


@pytest.mark.asyncio
async def test_hydrate_suggestions_pipeline_success_meta_and_id_paths() -> None:
    from search_api.services.suggestion_engine.hydration import EntityHydrator

    hydrator = EntityHydrator()

    ***REMOVED*** suggestions: "leo" uses meta type:id, "ali" uses id-only bytes
    suggestions = ["leo", "ali"]

    meta_results = ["actor:123", None]
    id_results = [None, b"456"]

    id_entities = [json.dumps({"id": 123, "name": "Leonardo", "type": "actor"}), None]

    redis = FakeRedis(
        get_map={},
        pipeline_results=meta_results + id_results + id_entities,
    )

    out = await hydrator.hydrate_suggestions(redis, suggestions, limit=10)
    assert len(out) == 2
    assert out[0]["id"] == 123
    assert out[0]["type"] == "actor"


@pytest.mark.asyncio
async def test_hydrate_suggestions_pipeline_failure_falls_back_to_sequential_gets() -> None:
    from search_api.services.suggestion_engine.hydration import EntityHydrator

    hydrator = EntityHydrator()

    suggestions = ["leo"]

    get_map = {
        "suggestions_meta:leo": "movie:not-an-int",  ***REMOVED*** forces parse failure
        "suggestions:leo": b"999",
        "entity:id:999": json.dumps({"id": 999, "title": "Leo", "type": "movie"}),
    }

    redis = FakeRedis(get_map=get_map, pipeline_results=[], raise_pipeline=True)

    out = await hydrator.hydrate_suggestions(redis, suggestions, limit=10)
    assert out[0]["id"] == 999
    assert out[0]["type"] == "movie"


@pytest.mark.asyncio
async def test_hydrate_suggestions_unresolved_name_fallback_minimal() -> None:
    from search_api.services.suggestion_engine.hydration import EntityHydrator

    hydrator = EntityHydrator()

    suggestions = ["unknown-title"]

    ***REMOVED*** pipeline returns meta None, id None, and no id_entities; name lookups all None
    redis = FakeRedis(get_map={}, pipeline_results=[None, None], raise_pipeline=False)

    out = await hydrator.hydrate_suggestions(redis, suggestions, limit=10)
    assert out[0]["text"] == "unknown-title"
    assert out[0]["type"] == "movie"


@pytest.mark.asyncio
async def test_hydrate_extra_suggestions_id_lookup_then_skip_duplicates() -> None:
    from search_api.services.suggestion_engine.hydration import EntityHydrator

    hydrator = EntityHydrator()

    get_map = {
        "suggestions:leo": b"111",
        "entity:id:111": json.dumps({"id": 111, "title": "Leo", "type": "movie"}),
    }
    redis = FakeRedis(get_map=get_map)

    out = await hydrator.hydrate_extra_suggestions(
        redis,
        extra_candidates=["leo", "leo"],
        suggestion_texts_seen=set(),
        seen_ids=set(),
        limit=10,
    )
    assert len(out) == 1
    assert out[0]["id"] == 111
