"""BFF Cache Warming Data Providers.

This module provides data sources for various warming strategies including
popularity data, user data, and recommendations.
"""

from datetime import datetime
from typing import Any, Dict, List

from config.logging import get_logger

from bff_api.config.app import get_settings
from bff_api.services.backend_client import BackendClient

logger = get_logger(__name__)


class BFFDataProviders:
    """Data providers for BFF warming strategies."""

    def __init__(self) -> None:
        """Initialize the data providers."""
        self.settings = get_settings()

    async def get_popularity_data(self) -> Dict[str, Any]:
        """Get BFF-specific popularity data for warming.

        Returns:
            Dictionary containing popular movies, actors, and genres
        """
        try:
            from bff_api.services.backend_client import BackendClient

            backend_client = BackendClient(config=self.settings)

            logger.debug(
                "Backend client created for popularity data",
                backend_url=self.settings.backend_api_url,
                service="bff",
                component="warming_providers",
            )

            logger.info(
                "Fetching popularity data for warming",
                service="bff",
                component="warming_providers",
            )

            ***REMOVED*** Get ALL movies from the backend API through pagination
            all_movies = await self._fetch_all_movies(backend_client)
            popular_actors = await self._get_popular_actors_data(backend_client)
            popular_genres = await self._get_popular_genres_data(backend_client)

            logger.info(
                "Successfully fetched popularity data",
                total_movies=len(all_movies),
                total_actors=len(popular_actors),
                total_genres=len(popular_genres),
                service="bff",
                component="warming_providers",
            )

            return {
                "movies": all_movies,
                "actors": popular_actors,
                "genres": popular_genres,
            }

        except Exception as e:
            logger.error(
                "Error getting BFF popularity data",
                error=str(e),
                service="bff",
                component="warming_providers",
            )
            return {"movies": [], "actors": [], "genres": []}

    async def _fetch_all_movies(self, backend_client: BackendClient) -> List[Dict[str, Any]]:
        """Fetch all movies from backend API through pagination."""
        all_movies = []
        page = 1
        page_size = 100

        while True:
            try:
                logger.debug(
                    "Fetching movies page for popularity data",
                    page=page,
                    page_size=page_size,
                    service="bff",
                    component="warming_providers",
                )

                movies_response = await backend_client.get_movies(
                    page=page,
                    limit=page_size,
                )

                page_movies = movies_response.get("results", [])

                if not page_movies:
                    break

                if not isinstance(page_movies, (list, tuple)):
                    logger.error(
                        "page_movies is not iterable",
                        type=type(page_movies).__name__,
                        value=str(page_movies),
                        service="bff",
                        component="warming_providers",
                    )
                    break

                ***REMOVED*** Transform movies to popularity format
                for movie in page_movies:
                    movie_id = movie.get("id")
                    if movie_id:
                        popularity_score = self._calculate_movie_popularity_score(movie)
                        view_count = self._estimate_movie_view_count(movie)

                        all_movies.append(
                            {
                                "id": movie_id,
                                "popularity_score": popularity_score,
                                "view_count": view_count,
                                "title": movie.get("title", "Unknown"),
                                "release_date": movie.get("release_date"),
                            }
                        )

                if not movies_response.get("has_next", False):
                    break

                page += 1

                ***REMOVED*** Safety limit
                if page > 1000:
                    logger.warning(
                        "Reached maximum page limit for movie fetching",
                        max_pages=1000,
                        service="bff",
                        component="warming_providers",
                    )
                    break

            except Exception as e:
                logger.error(
                    "Error fetching movies page for popularity data",
                    page=page,
                    error=str(e),
                    service="bff",
                    component="warming_providers",
                )
                break

        return all_movies

    def _calculate_movie_popularity_score(self, movie: Dict[str, Any]) -> float:
        """Calculate popularity score for a movie based on available data."""
        try:
            score = 1.0

            ***REMOVED*** Boost based on ratings
            imdb_rating = movie.get("imdb_rating")
            if imdb_rating and imdb_rating > 7.0:
                score += (imdb_rating - 7.0) * 0.5

            rotten_tomatoes = movie.get("rotten_tomatoes_rating")
            if rotten_tomatoes and rotten_tomatoes > 80:
                score += (rotten_tomatoes - 80) * 0.01

            ***REMOVED*** Boost recent movies (released in last 5 years)
            release_date = movie.get("release_date")
            if release_date:
                try:
                    release_year = datetime.fromisoformat(release_date.replace("Z", "+00:00")).year
                    current_year = datetime.now().year
                    if current_year - release_year <= 5:
                        score += 0.5
                except:
                    pass

            ***REMOVED*** Boost movies with higher vote counts
            vote_count = movie.get("vote_count", 0)
            if vote_count > 1000:
                score += min(vote_count / 10000, 1.0)

            return round(score, 2)

        except Exception:
            return 1.0

    def _estimate_movie_view_count(self, movie: Dict[str, Any]) -> int:
        """Estimate view count based on available movie data."""
        try:
            views = 100

            vote_count = movie.get("vote_count", 0)
            if vote_count:
                views = max(vote_count * 10, 100)

            imdb_rating = movie.get("imdb_rating", 0)
            if imdb_rating and imdb_rating > 8.0:
                views = int(views * 1.5)

            return views

        except Exception:
            return 100

    async def _get_popular_actors_data(self, backend_client: BackendClient) -> List[Dict[str, Any]]:
        """Get popular actors data for warming."""
        try:
            popular_actors = [
                {"id": 1, "popularity_score": 8.5, "view_count": 5000},
                {"id": 2, "popularity_score": 8.2, "view_count": 4500},
                {"id": 3, "popularity_score": 7.8, "view_count": 4000},
                {"id": 4, "popularity_score": 7.5, "view_count": 3500},
                {"id": 5, "popularity_score": 7.2, "view_count": 3000},
            ]

            logger.info(
                "Retrieved popular actors data",
                actor_count=len(popular_actors),
                service="bff",
                component="warming_providers",
            )

            return popular_actors

        except Exception as e:
            logger.error(
                "Error getting popular actors data",
                error=str(e),
                service="bff",
                component="warming_providers",
            )
            return []

    async def _get_popular_genres_data(self, backend_client: BackendClient) -> List[Dict[str, Any]]:
        """Get all genres data for warming."""
        try:
            ***REMOVED*** Fetch all genres from backend API
            genres = await backend_client.get_genres()

            ***REMOVED*** Transform genres for warming cache with default popularity data
            popular_genres = []
            for genre in genres:
                genre_id = genre.get("id")
                if genre_id:
                    ***REMOVED*** Calculate popularity score based on genre ID (simple heuristic)
                    ***REMOVED*** Action, Comedy, Drama tend to be more popular
                    base_score = 5.0
                    if genre_id in [28, 35, 18]:  ***REMOVED*** Action, Comedy, Drama
                        base_score = 8.0
                    elif genre_id in [27, 53, 10749]:  ***REMOVED*** Horror, Thriller, Romance
                        base_score = 6.5
                    elif genre_id in [878, 12, 16]:  ***REMOVED*** Sci-Fi, Adventure, Animation
                        base_score = 6.0

                    ***REMOVED*** Estimate view count based on popularity score
                    view_count = int(base_score * 500)

                    popular_genres.append(
                        {
                            "id": genre_id,
                            "name": genre.get("name", "Unknown"),
                            "popularity_score": base_score,
                            "view_count": view_count,
                        }
                    )

            logger.info(
                "Retrieved all genres data for warming",
                genre_count=len(popular_genres),
                service="bff",
                component="warming_providers",
            )

            return popular_genres

        except Exception as e:
            logger.error(
                "Error getting genres data from backend",
                error=str(e),
                service="bff",
                component="warming_providers",
            )
            return []

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get BFF-specific user profile data.

        Args:
            user_id: User ID to get data for

        Returns:
            Dictionary containing user preferences and behavior data
        """
        try:
            ***REMOVED*** In production: query BFF user service, preferences, history
            return {
                "watchlist": [1, 2, 3, 254, 550],
                "favorite_genres": [28, 12, 16, 35, 80],
                "recently_viewed": [680, 13, 24, 155, 122],
                "favorite_actors": [1, 2, 3, 4, 5],
                "preferred_decades": ["2020s", "2010s", "1990s"],
            }
        except Exception as e:
            logger.error(f"Error getting BFF user data for {user_id}: {e}")
            return {}

    async def get_user_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get BFF-specific user recommendations.

        Args:
            user_id: User ID to get recommendations for

        Returns:
            List of recommended items with confidence scores
        """
        try:
            ***REMOVED*** In production: query BFF recommendation engine
            return [
                {"movie_id": 680, "confidence": 0.95, "type": "collaborative"},
                {"movie_id": 13, "confidence": 0.88, "type": "content"},
                {"movie_id": 24, "confidence": 0.82, "type": "collaborative"},
            ]
        except Exception as e:
            logger.error(f"Error getting BFF recommendations for {user_id}: {e}")
            return []
