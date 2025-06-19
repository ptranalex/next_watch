"""BFF Cache Warming Functions.

This module implements the actual warming functions that call cached BFF endpoints
to populate the cache with real data.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from config.logging import get_logger

from bff_api.config.app import settings

logger = get_logger(__name__)


class BFFWarmingFunctions:
    """BFF-specific warming function implementations."""

    def __init__(self) -> None:
        """Initialize the warming functions."""
        self.settings = settings

    async def warm_movie_screen(
        self, movie_id: int, user_id: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm BFF movie screen data.

        This function demonstrates the complete warming integration pattern by:
        1. Importing and calling the actual cached function
        2. Handling dependencies (backend client, credentials)
        3. Supporting both anonymous and authenticated warming
        4. Providing proper error handling and logging

        Args:
            movie_id: Movie ID to warm
            user_id: Optional user ID for user-specific warming
            **kwargs: Additional parameters from warming strategies

        Returns:
            Dictionary containing the warmed data

        Raises:
            Exception: If warming operation fails
        """
        try:
            from bff_api.routes.v1.movies import _get_movie_screen_data
            from bff_api.services.backend_client import BackendClient

            logger.info(
                "Starting movie screen warming",
                movie_id=movie_id,
                user_id=user_id,
                service="bff",
                component="warming_functions",
            )

            ***REMOVED*** Create backend client instance for warming
            backend_client = BackendClient(config=self.settings)

            ***REMOVED*** For warming, we don't have actual HTTP credentials
            ***REMOVED*** This warming call will populate cache for the specific user_id (or anonymous if None)
            credentials = None  ***REMOVED*** Warming operates without active user sessions

            ***REMOVED*** Call the actual cached function - this will populate the cache
            ***REMOVED*** The @redis_cache decorator will handle cache storage
            warmed_data = await _get_movie_screen_data(
                movie_id=movie_id,
                user_id=user_id,
                backend=backend_client,
                credentials=credentials,
            )

            ***REMOVED*** Log successful warming with metrics
            logger.info(
                "Successfully warmed movie screen data",
                movie_id=movie_id,
                user_id=user_id,
                has_movie_data=bool(warmed_data.get("movie")),
                cast_count=len(warmed_data.get("cast", [])),
                trailer_count=len(warmed_data.get("trailers", [])),
                similar_movies_count=len(warmed_data.get("similar_movies", [])),
                service="bff",
                component="warming_functions",
            )

            ***REMOVED*** Return summary data for warming statistics
            return {
                "movie_id": movie_id,
                "user_id": user_id,
                "warmed_data_keys": list(warmed_data.keys()),
                "cache_populated": True,
                "warming_type": "movie_screen",
                "timestamp": datetime.now().isoformat(),
            }

        except ImportError as e:
            logger.error(
                "Failed to import required modules for movie screen warming",
                movie_id=movie_id,
                user_id=user_id,
                error=str(e),
                service="bff",
                component="warming_functions",
            )
            raise Exception(f"Import error during movie screen warming: {e}")

        except Exception as e:
            logger.error(
                "Failed to warm movie screen data",
                movie_id=movie_id,
                user_id=user_id,
                error=str(e),
                service="bff",
                component="warming_functions",
            )
            raise Exception(f"Movie screen warming failed: {e}")

    async def warm_movies_list(
        self, page: int = 1, limit: int = 20, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm BFF movies list data.

        Example implementation following the movie screen pattern.
        This could be enhanced to warm different filter combinations.
        """
        try:
            from bff_api.routes.v1.movies import _get_movies_list_data
            from bff_api.services.backend_client import BackendClient

            logger.info(
                "Starting movies list warming",
                page=page,
                limit=limit,
                service="bff",
                component="warming_functions",
            )

            backend_client = BackendClient(config=self.settings)

            ***REMOVED*** Extract warming parameters from kwargs
            genre_id = kwargs.get("genre_id")
            actor_id = kwargs.get("actor_id")
            sort_by = kwargs.get("sort_by")
            sort_desc = kwargs.get("sort_desc", True)
            user_id = kwargs.get("user_id")

            ***REMOVED*** Warm the movies list cache
            warmed_data = await _get_movies_list_data(
                page=page,
                limit=limit,
                genre_id=genre_id,
                actor_id=actor_id,
                sort_by=sort_by,
                sort_desc=sort_desc,
                imdb_rating=kwargs.get("imdb_rating"),
                rotten_tomatoes_rating=kwargs.get("rotten_tomatoes_rating"),
                metacritic_rating=kwargs.get("metacritic_rating"),
                year=kwargs.get("year"),
                start_year=kwargs.get("start_year"),
                end_year=kwargs.get("end_year"),
                user_id=user_id,
                backend=backend_client,
                credentials=None,
            )

            logger.info(
                "Successfully warmed movies list data",
                page=page,
                limit=limit,
                total_movies=len(warmed_data.get("results", [])),
                service="bff",
                component="warming_functions",
            )

            return {
                "page": page,
                "limit": limit,
                "filters": {k: v for k, v in kwargs.items() if v is not None},
                "movies_count": len(warmed_data.get("results", [])),
                "cache_populated": True,
                "warming_type": "movies_list",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                "Failed to warm movies list data",
                page=page,
                limit=limit,
                error=str(e),
                service="bff",
                component="warming_functions",
            )
            raise Exception(f"Movies list warming failed: {e}")

    async def warm_actor_screen(
        self, actor_id: int, page: int = 1, limit: int = 20, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm BFF actor screen data.

        This function calls the actual cached actor screen function to populate the cache.

        Args:
            actor_id: Actor ID to warm
            page: Page number for pagination
            limit: Items per page
            **kwargs: Additional parameters from warming strategies

        Returns:
            Dictionary containing the warmed data summary

        Raises:
            Exception: If warming operation fails
        """
        try:
            from bff_api.routes.v1.actors import _get_actor_screen_data
            from bff_api.services.backend_client import BackendClient

            logger.info(
                "Starting actor screen warming",
                actor_id=actor_id,
                page=page,
                limit=limit,
                service="bff",
                component="warming_functions",
            )

            backend_client = BackendClient(config=self.settings)

            ***REMOVED*** Call the actual cached function to populate the cache
            warmed_data = await _get_actor_screen_data(
                actor_id=actor_id,
                page=page,
                limit=limit,
                backend=backend_client,
                credentials=None,
            )

            logger.info(
                "Successfully warmed actor screen data",
                actor_id=actor_id,
                page=page,
                limit=limit,
                actor_name=warmed_data.get("actor", {}).get("name", "Unknown"),
                movies_count=len(warmed_data.get("movies", {}).get("results", [])),
                service="bff",
                component="warming_functions",
            )

            return {
                "actor_id": actor_id,
                "page": page,
                "limit": limit,
                "actor_name": warmed_data.get("actor", {}).get("name", "Unknown"),
                "movies_count": len(warmed_data.get("movies", {}).get("results", [])),
                "cache_populated": True,
                "warming_type": "actor_screen",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                "Failed to warm actor screen data",
                actor_id=actor_id,
                page=page,
                limit=limit,
                error=str(e),
                service="bff",
                component="warming_functions",
            )
            raise Exception(f"Actor screen warming failed: {e}")

    async def warm_genre_screen(
        self, genre_id: int, sort_by: str = "imdb_rating", page: int = 1, **kwargs: Any
    ) -> Dict[str, Any]:
        """Warm BFF genre screen data.

        This function calls the actual cached genre screen function to populate the cache.

        Args:
            genre_id: Genre ID to warm
            sort_by: Sort criteria for movies in genre
            page: Page number for pagination
            **kwargs: Additional parameters from warming strategies

        Returns:
            Dictionary containing the warmed data summary

        Raises:
            Exception: If warming operation fails
        """
        try:
            from bff_api.routes.v1.genres import _get_genre_screen_data
            from bff_api.services.backend_client import BackendClient

            logger.info(
                "Starting genre screen warming",
                genre_id=genre_id,
                sort_by=sort_by,
                page=page,
                service="bff",
                component="warming_functions",
            )

            backend_client = BackendClient(config=self.settings)

            ***REMOVED*** Extract additional parameters
            limit = kwargs.get("limit", 20)

            ***REMOVED*** Call the actual cached function to populate the cache
            warmed_data = await _get_genre_screen_data(
                genre_id=genre_id,
                page=page,
                limit=limit,
                actor_id=kwargs.get("actor_id"),
                sort_by=sort_by,
                sort_desc=kwargs.get("sort_desc", True),
                imdb_rating=kwargs.get("imdb_rating"),
                rotten_tomatoes_rating=kwargs.get("rotten_tomatoes_rating"),
                metacritic_rating=kwargs.get("metacritic_rating"),
                year=kwargs.get("year"),
                start_year=kwargs.get("start_year"),
                end_year=kwargs.get("end_year"),
                user_id=kwargs.get("user_id"),
                backend=backend_client,
                credentials=None,
            )

            logger.info(
                "Successfully warmed genre screen data",
                genre_id=genre_id,
                sort_by=sort_by,
                page=page,
                genre_name=warmed_data.get("genre", {}).get("name", "Unknown"),
                movies_count=len(warmed_data.get("movies", {}).get("results", [])),
                service="bff",
                component="warming_functions",
            )

            return {
                "genre_id": genre_id,
                "sort_by": sort_by,
                "page": page,
                "genre_name": warmed_data.get("genre", {}).get("name", "Unknown"),
                "movies_count": len(warmed_data.get("movies", {}).get("results", [])),
                "cache_populated": True,
                "warming_type": "genre_screen",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                "Failed to warm genre screen data",
                genre_id=genre_id,
                sort_by=sort_by,
                page=page,
                error=str(e),
                service="bff",
                component="warming_functions",
            )
            raise Exception(f"Genre screen warming failed: {e}")

    async def warm_user_dashboard(self, user_id: int, **kwargs: Any) -> Dict[str, Any]:
        """Warm BFF user dashboard data."""
        logger.debug(f"Warming user dashboard for user {user_id}")
        return {"user_id": user_id, "dashboard": "warmed"}

    async def warm_homepage(self, **kwargs: Any) -> Dict[str, Any]:
        """Warm BFF homepage data."""
        logger.debug("Warming homepage data")
        return {"homepage": "warmed"}
