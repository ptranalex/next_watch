"""Backend data provider used during indexing.

Abstracts the details of fetching movies/actors from Backend API so the
indexer can remain decoupled from HTTP and response formats.
"""

from typing import Any

from config.logging import get_logger

from search_api.services.backend_client import BackendAPIClient

logger = get_logger(__name__)


class BackendProvider:
    """Fetches entities from Backend API for indexing."""

    def __init__(self, config: Any) -> None:
        self._client = BackendAPIClient(config)

    async def fetch_movies(self, limit: int | None) -> list[dict[str, Any]]:
        movies: list[dict[str, Any]] = []
        page = 1
        page_size = 100
        effective_limit = limit if limit is not None else 999_999

        while len(movies) < effective_limit:
            remaining = effective_limit - len(movies)
            current_page_size = min(remaining, page_size)
            try:
                response = await self._client.list_movies(
                    page=page,
                    limit=current_page_size,
                    sort_by="imdb_rating",
                    sort_desc=True,
                )
                page_movies = response.get("results", [])
            except Exception as e:  ***REMOVED*** pragma: no cover - defensive
                logger.warning(f"Movies endpoint failed, using fallback: {e}")
                response = await self._client.search_movies(
                    query="e",
                    page=page,
                    limit=current_page_size,
                    sort_by="imdb_rating",
                    sort_desc=True,
                )
                page_movies = response.get("results", [])

            if not page_movies:
                break

            for movie in page_movies:
                movies.append(
                    {
                        "id": movie.get("id"),
                        "title": movie.get("title"),
                        "poster_path": movie.get("poster_url"),
                        "release_date": movie.get("release_date"),
                        "popularity": movie.get("popularity"),
                        "vote_average": movie.get("vote_average"),
                        "release_year": int(movie.get("release_date", "0000")[:4])
                        if movie.get("release_date")
                        else None,
                    }
                )

                if limit is not None and len(movies) >= limit:
                    break

            page += 1
            if limit is None and page > 200:
                logger.warning("Reached maximum page limit (200) for fetch-all")
                break
            if limit is not None and page > 50:
                logger.warning("Reached maximum page limit (50) for limited fetch")
                break

        return movies

    async def fetch_actors(self, limit: int) -> list[dict[str, Any]]:
        actors: list[dict[str, Any]] = []
        page = 1
        while len(actors) < limit:
            remaining = limit - len(actors)
            current_page_size = min(remaining, 100)
            response = await self._client.list_actors(page=page, limit=current_page_size)
            page_actors = response.get("actors", [])
            if not page_actors:
                break
            for actor in page_actors:
                actors.append(
                    {
                        "id": actor.get("id"),
                        "name": actor.get("name"),
                        "profile_path": actor.get("profile_path"),
                        "popularity": actor.get("popularity"),
                        "gender": actor.get("gender"),
                    }
                )
                if len(actors) >= limit:
                    break
            page += 1
            if page > 50:
                logger.warning("Reached maximum page limit (50) for actors")
                break
        return actors
