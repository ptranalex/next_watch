"""Suggestion indexer - orchestrates fetching and writing suggestion data.

This module contains no CLI/output code so it can be reused from jobs/tests.
"""

from .models import IndexOptions, IndexStats
from .providers.backend_provider import BackendProvider
from .providers.redis_store import RedisStore


class SuggestionIndexer:
    """High-level indexer that coordinates providers and storage."""

    def __init__(self, backend: BackendProvider, store: RedisStore) -> None:
        self._backend = backend
        self._store = store

    async def populate(self, options: IndexOptions) -> IndexStats:
        if options.clear_existing:
            await self._store.clear_suggestions_and_entities()

        stats = IndexStats()

        if options.include_movies:
            movies = await self._backend.fetch_movies(limit=options.fetch_limit)
            stats.movies_indexed = await self._store.index_movies(
                movies,
                include_words=options.include_words,
                min_word_length=options.min_word_length,
                batch_size=options.batch_size,
            )

        if options.include_actors:
            actors = await self._backend.fetch_actors(limit=500)
            stats.actors_indexed = await self._store.index_actors(
                actors, batch_size=options.batch_size
            )

        ***REMOVED*** Directors can be added when backend supports it

        counts = await self._store.counts()
        stats.zset_entries = counts.get("zset", 0)
        stats.entity_records = counts.get("entities", 0)
        return stats
