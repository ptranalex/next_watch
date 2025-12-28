"""Movie data adapter for the Recommendation API.

This module provides a MovieDataAdapter class that adapts the backend API
to provide movie data for the recommendation service.
"""

from typing import Any

from config.logging import get_logger

from recommendation_api.models.recommendation import MovieRecommendation
from recommendation_api.services.backend_client import BackendClient, get_backend_client

logger = get_logger(__name__)


class MovieDataAdapter:
    """Adapter for movie data from backend API."""

    def __init__(self, backend_client: BackendClient | None = None):
        """Initialize the movie data adapter.

        Args:
            backend_client: Optional backend client. If None, will create a new client.
        """
        self.backend_client = backend_client or get_backend_client()

    def _convert_to_recommendation(
        self, movie_data: dict[str, Any], reason: str = "", score: float = 0.0
    ) -> MovieRecommendation:
        """Convert movie data to a MovieRecommendation object.

        Args:
            movie_data: Movie data from backend API or vector DB metadata
            reason: Recommendation reason
            score: Recommendation score (0-1)

        Returns:
            MovieRecommendation object
        """
        ***REMOVED*** Extract movie ID, defaulting to None if not found
        movie_id = movie_data.get("id") or movie_data.get("movie_id")

        ***REMOVED*** Process genres - extract names if they're dictionaries
        genres = movie_data.get("genres", [])
        processed_genres = []

        if genres:
            for genre in genres:
                if isinstance(genre, dict) and "name" in genre:
                    ***REMOVED*** Extract name from genre dictionary
                    processed_genres.append(genre["name"])
                elif isinstance(genre, str):
                    ***REMOVED*** Already a string
                    processed_genres.append(genre)
                else:
                    ***REMOVED*** Try to convert to string as fallback
                    try:
                        processed_genres.append(str(genre))
                    except Exception:
                        logger.warning(f"Could not process genre: {genre}")

        ***REMOVED*** Ensure score is within valid range (0.0 to 1.0)
        clamped_score = min(max(0.0, score), 1.0)
        if score != clamped_score:
            logger.debug(f"Clamped score from {score} to {clamped_score}")

        ***REMOVED*** Handle both API response format and vector DB metadata format
        ***REMOVED*** Ensure we always provide an int ID to the response model.
        try:
            movie_id_int = int(movie_id or 0)
        except Exception:
            movie_id_int = 0

        return MovieRecommendation(
            id=movie_id_int,
            title=movie_data.get("title", "Unknown"),
            poster_url=movie_data.get("poster_path") or movie_data.get("poster_url"),
            overview=movie_data.get("overview", ""),
            release_date=movie_data.get("release_date"),
            imdb_rating=movie_data.get("imdb_rating", 0.0),
            tmdb_rating=movie_data.get("vote_average", 0.0),
            genres=processed_genres,
            reason=reason,
            score=clamped_score,
        )

    async def get_movie_by_id(self, movie_id: int) -> dict[str, Any] | None:
        """Get a movie by ID from the backend API.

        Args:
            movie_id: Movie ID

        Returns:
            Movie data or None if not found
        """
        try:
            return await self.backend_client.get_movie(movie_id)
        except Exception as e:
            logger.error(f"Error getting movie {movie_id}: {e}")
            return None

    async def get_movies_by_ids(self, movie_ids: list[int]) -> list[dict[str, Any]]:
        """Get multiple movies by IDs from the backend API.

        Args:
            movie_ids: List of movie IDs

        Returns:
            List of movie data dictionaries
        """
        try:
            return await self.backend_client.get_movies_batch(movie_ids)
        except Exception as e:
            logger.error(f"Error getting movies batch: {e}")
            return []

    async def get_popular_movies(
        self, limit: int = 20, min_rating: float = 7.0, min_vote_count: int = 1000
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get popular movies from the backend API.

        Args:
            limit: Maximum number of movies
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count

        Returns:
            Tuple of (movie recommendations, filters)
        """
        try:
            ***REMOVED*** Call backend API to get popular movies
            popular_movies = await self.backend_client.get_popular_movies(
                limit=limit, min_rating=min_rating, min_vote_count=min_vote_count
            )

            ***REMOVED*** Convert to recommendation objects
            recommendations = [
                self._convert_to_recommendation(
                    movie, "Popular on Next Watch", movie.get("vote_average", 0.0) / 10.0
                )
                for movie in popular_movies
            ]

            ***REMOVED*** Return recommendations with filters
            return recommendations, {
                "limit": limit,
                "min_rating": min_rating,
                "min_vote_count": min_vote_count,
                "type": "popular",
            }

        except Exception as e:
            logger.error(f"Error getting popular movies: {e}")
            return [], {"error": str(e)}

    async def get_personalized_movies(
        self, user_id: int, limit: int = 20, min_rating: float = 7.0, min_vote_count: int = 1000
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get personalized movie recommendations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count

        Returns:
            Tuple of (movie recommendations, filters)
        """
        try:
            ***REMOVED*** Call backend API to get personalized movies
            personalized_movies = await self.backend_client.get_personalized_movies(
                user_id=user_id, limit=limit, min_rating=min_rating, min_vote_count=min_vote_count
            )

            ***REMOVED*** Convert to recommendation objects
            recommendations = [
                self._convert_to_recommendation(
                    movie,
                    movie.get("reason", "Recommended for you"),
                    movie.get("score", movie.get("vote_average", 0.0) / 10.0),
                )
                for movie in personalized_movies
            ]

            ***REMOVED*** Return recommendations with filters
            return recommendations, {
                "user_id": user_id,
                "limit": limit,
                "min_rating": min_rating,
                "min_vote_count": min_vote_count,
                "type": "personalized",
            }

        except Exception as e:
            logger.error(f"Error getting personalized movies for user {user_id}: {e}")
            return [], {"error": str(e)}

    async def get_trending_movies(
        self, limit: int = 20, days: int = 7
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get trending movies from the backend API.

        Args:
            limit: Maximum number of movies
            days: Time window in days

        Returns:
            Tuple of (movie recommendations, filters)
        """
        try:
            ***REMOVED*** Call backend API to get trending movies
            ***REMOVED*** Note: This endpoint might not exist yet in the backend API
            trending_movies = await self.backend_client.get_trending_movies(limit=limit, days=days)

            ***REMOVED*** Convert to recommendation objects
            recommendations = [
                self._convert_to_recommendation(
                    movie,
                    f"Trending in the last {days} days",
                    movie.get("vote_average", 0.0) / 10.0,
                )
                for movie in trending_movies
            ]

            ***REMOVED*** Return recommendations with filters
            return recommendations, {
                "limit": limit,
                "days": days,
                "type": "trending",
            }

        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            ***REMOVED*** For warming purposes, return empty list rather than raising
            return [], {"error": str(e)}

    async def get_recent_movies(
        self, limit: int = 20
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get recently updated movies from the backend API.

        Args:
            limit: Maximum number of movies

        Returns:
            Tuple of (movie recommendations, filters)
        """
        try:
            ***REMOVED*** Call backend API to get recent movies
            ***REMOVED*** Note: This endpoint might not exist yet in the backend API
            recent_movies = await self.backend_client.get_recent_movies(limit=limit)

            ***REMOVED*** Convert to recommendation objects
            recommendations = [
                self._convert_to_recommendation(
                    movie, "Recently updated", movie.get("vote_average", 0.0) / 10.0
                )
                for movie in recent_movies
            ]

            ***REMOVED*** Return recommendations with filters
            return recommendations, {
                "limit": limit,
                "type": "recent",
            }

        except Exception as e:
            logger.error(f"Error getting recent movies: {e}")
            ***REMOVED*** For warming purposes, return empty list rather than raising
            return [], {"error": str(e)}


***REMOVED*** Global movie adapter instance
_movie_adapter: MovieDataAdapter | None = None


def get_movie_adapter() -> MovieDataAdapter:
    """Get or create a global movie adapter instance.

    This function can be used as a FastAPI dependency.

    Returns:
        MovieDataAdapter instance
    """
    global _movie_adapter

    if _movie_adapter is None:
        ***REMOVED*** Create a new movie adapter with the global backend client
        _movie_adapter = MovieDataAdapter(get_backend_client())

    return _movie_adapter
