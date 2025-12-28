"""Unit tests for Search API scoped modules (config + suggestion_engine pieces)."""

from __future__ import annotations

import pytest


def test_fast_core_config_adapter() -> None:
    from search_api.config.app import SearchAPIConfig
    from search_api.config.fast_core_config import create_fast_core_config

    cfg = SearchAPIConfig(debug=True, ml_api_url=None)
    fc = create_fast_core_config(cfg)

    assert fc.service_name == "search-api"
    ***REMOVED*** ml url filtered out when None
    assert fc.get_service_url("ml") is None


def test_utils_helpers() -> None:
    from search_api.services.suggestion_engine.utils import (
        build_image_url,
        format_suggestions,
        normalize_query,
    )

    assert normalize_query("  HeLLo ") == "hello"
    assert format_suggestions(["a"]) == [{"text": "a", "score": 1.0}]
    assert build_image_url(None) is None
    assert build_image_url("http://x") == "http://x"
    assert build_image_url("/p.jpg").endswith("/p.jpg")


def test_ranker_sort_and_merge() -> None:
    from search_api.services.suggestion_engine.ranking import SuggestionRanker

    suggs = [
        {"text": "leonardo", "popularity": 10},
        {"text": "leo", "popularity": 1},
        {"text": "napoleon", "popularity": 100},
    ]

    sorted_s = SuggestionRanker.sort_suggestions(suggs, query_prefix="leo")
    ***REMOVED*** exact match should be first
    assert sorted_s[0]["text"] == "leo"

    enhanced = SuggestionRanker.enhance_with_search_metadata(
        [{"text": "Leo"}, {"text": "Napoleon"}], query="leo"
    )
    assert enhanced[0]["search_type"] == "exact"

    merged = SuggestionRanker.merge_unique_suggestions(
        primary_suggestions=[{"text": "a"}],
        additional_suggestions=[{"text": "A"}, {"text": "b"}],
        limit=2,
        mark_additional_as_fuzzy=True,
    )
    assert len(merged) == 2
    assert merged[1]["text"].lower() == "b"


@pytest.mark.asyncio
async def test_entity_hydrator_build_and_hydrate() -> None:
    from search_api.services.suggestion_engine.hydration import EntityHydrator

    hydrator = EntityHydrator()

    ***REMOVED*** Direct helper path
    obj = hydrator._build_suggestion_object(
        text="t",
        entity_type="movie",
        entity_data={"id": 1, "title": "T", "poster_url": "/p.jpg", "popularity": 1.0},
    )
    assert obj["id"] == 1
    assert obj["image_path"].endswith("/p.jpg")

    class FakePipeline:
        def __init__(self):
            self.keys = []

        def get(self, k):
            self.keys.append(k)
            return self

        async def execute(self):
            ***REMOVED*** return meta (type:id) then id
            return ["movie:1", "1"]

    class FakeRedis:
        def pipeline(self):
            return FakePipeline()

        async def get(self, k):
            if k == "entity:id:1":
                return '{"id": 1, "title": "T", "poster_url": "/p.jpg", "popularity": 1.0}'
            return None

    res = await hydrator.hydrate_suggestions(FakeRedis(), ["t"], limit=5)
    assert res and res[0]["id"] == 1
