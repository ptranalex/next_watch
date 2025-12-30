"""Unit tests for utility helpers in movie sync.

The sync module imports `movie_storage` at import time. In the monorepo that
package is a sibling lib, but it may not be installed in this test environment.

To keep these tests lightweight, we stub minimal `movie_storage.*` modules in
`sys.modules` before importing `data_importer.sync.movie_sync`.
"""

import sys
import types

import pytest


def _install_movie_storage_stubs() -> None:
    # Provide minimal functions that data_importer imports.
    def _noop(*args, **kwargs):
        return None

    movie_storage = types.ModuleType("movie_storage")

    db = types.ModuleType("movie_storage.db")
    operations = types.ModuleType("movie_storage.db.operations")
    operations_movie = types.ModuleType("movie_storage.db.operations.movie")

    operations.get_movie_by_id = _noop
    operations.get_movie_by_tmdb_id = _noop
    operations.update_movie = _noop

    operations_movie.create_movie_from_tmdb_details = _noop

    models = types.ModuleType("movie_storage.models")

    class Movie:  # minimal placeholder
        pass

    models.Movie = Movie

    sys.modules.setdefault("movie_storage", movie_storage)
    sys.modules.setdefault("movie_storage.db", db)
    sys.modules.setdefault("movie_storage.db.operations", operations)
    sys.modules.setdefault("movie_storage.db.operations.movie", operations_movie)
    sys.modules.setdefault("movie_storage.models", models)


_install_movie_storage_stubs()

from data_importer.sync.movie_sync import convert_string_to_date, fetch_genre_data  # noqa: E402


def test_convert_string_to_date_valid() -> None:
    d = convert_string_to_date("2024-01-31")
    assert d is not None
    assert (d.year, d.month, d.day) == (2024, 1, 31)


def test_convert_string_to_date_invalid_returns_none() -> None:
    assert convert_string_to_date("not-a-date") is None
    assert convert_string_to_date(None) is None


@pytest.mark.asyncio
async def test_fetch_genre_data_builds_id_map() -> None:
    class FakeTMDB:
        async def get_movie_genres(self):
            return [
                {"id": 28, "name": "Action"},
                {"id": 18, "name": "Drama"},
                {"id": None, "name": "Ignored"},
            ]

    genre_map = await fetch_genre_data(FakeTMDB())
    assert genre_map[28]["name"] == "Action"
    assert genre_map[18]["name"] == "Drama"
    assert None not in genre_map
