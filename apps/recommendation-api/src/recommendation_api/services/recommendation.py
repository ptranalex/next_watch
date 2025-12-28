"""Recommendation service for the Recommendation API.

This module provides functionality for generating movie recommendations
based on various criteria and user preferences.
"""

import time
from typing import Any

from config.logging import get_logger
from fast_core.errors import (
    ValidationException,
    critical_service_handler,
    optional_service_handler,
)

***REMOVED*** Remove movie_storage dependency - now using API-based approach
from recommendation_api.models.recommendation import MovieRecommendation

***REMOVED*** Replace local embedding import with ML API client
***REMOVED*** from recommendation_api.services.embedding import generate_user_preference_vector
from recommendation_api.services.ml_api_client import get_ml_api_client
from recommendation_api.services.movie_adapter import MovieDataAdapter

***REMOVED*** No longer importing database operations - using API-based approach via MovieDataAdapter
from recommendation_api.services.vector_service import VectorService, get_vector_service

logger = get_logger(__name__)


class RecommendationService:
    """Service for generating movie recommendations."""

    def __init__(
        self, movie_adapter: MovieDataAdapter, vector_service: VectorService | None = None
    ):
        """Initialize the recommendation service.

        Args:
            movie_adapter: Movie data adapter for API communication
            vector_service: Vector service for similarity searches
        """
        self.movie_adapter = movie_adapter
        self.vector_service = vector_service or get_vector_service()

    ***REMOVED*** Comment out methods that use unavailable functions
    """
    def get_trending_recommendations(
        self,
        limit: int = 20,
        days: int = 7,
        min_rating: Optional[float] = None,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        ***REMOVED*** ...
    """

    """
    def get_popular_recommendations(
        self,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        ***REMOVED*** ...
    """

    @optional_service_handler(
        service_name="backend-api",
        logger=logger,
        fallback_value=([], {"error": "Popular movies unavailable", "graceful_degradation": True}),
        operation_name="get_popular_movies",
    )
    async def get_popular_recommendations_direct(
        self,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get popular movie recommendations using the backend API.

        This now uses the MovieDataAdapter to fetch data from backend-api
        instead of direct database queries.

        Uses graceful degradation - returns empty list if backend is unavailable.

        Args:
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating threshold
            min_vote_count: Minimum vote count threshold

        Returns:
            Tuple of (recommendations list, filters dict) with graceful fallback

        Raises:
            ValidationException: If parameters are invalid
        """
        ***REMOVED*** Validate parameters
        if limit <= 0:
            raise ValidationException("Limit must be positive")
        if min_rating < 0 or min_rating > 10:
            raise ValidationException("Minimum rating must be between 0 and 10")
        if min_vote_count < 0:
            raise ValidationException("Minimum vote count must be non-negative")

        logger.info(
            "Fetching popular movies from backend API",
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
            service="recommendation-api",
            component="recommendation_service",
            operation="get_popular_movies",
        )

        ***REMOVED*** Get popular movies from backend API via adapter
        return await self.movie_adapter.get_popular_movies(
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )

    @critical_service_handler(
        service_name="backend-api", logger=logger, operation_name="get_user_recommendations"
    )
    async def get_user_recommendations_direct(
        self,
        user_id: int,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get personalized movie recommendations using the backend API.

        This now uses the MovieDataAdapter to fetch data from backend-api
        instead of direct database queries.

        Args:
            user_id: User ID to get recommendations for
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating threshold
            min_vote_count: Minimum vote count threshold

        Returns:
            Tuple of (recommendations list, filters dict)
        """
        ***REMOVED*** Validate user ID
        if user_id <= 0:
            raise ValueError(f"Invalid user ID: {user_id}")

        ***REMOVED*** Get personalized recommendations from backend API via adapter
        return await self.movie_adapter.get_personalized_movies(
            user_id=user_id,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )

    """
    def get_user_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        ***REMOVED*** ...
    """

    @optional_service_handler(
        service_name="vector-qdrant",
        logger=logger,
        fallback_value=([], {"error": "Similar movies unavailable", "graceful_degradation": True}),
        operation_name="get_similar_movies",
    )
    async def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20,
        min_rating: float = 6.0,
        min_vote_count: int = 500,
        min_score: float = 0.01,
    ) -> tuple[list[MovieRecommendation], dict[str, Any]]:
        """Get similar movies based on vector similarity.

        Uses graceful degradation - returns empty list if vector service is unavailable.

        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count threshold (DEPRECATED - not available in backend API)
            min_score: Minimum similarity score

        Returns:
            Tuple of (recommendations list, filters dict) with graceful fallback

        Raises:
            ValidationException: If movie_id or other parameters are invalid
            ResourceNotFoundException: If movie is not found
        """
        ***REMOVED*** Validate parameters
        if movie_id <= 0:
            raise ValidationException("Movie ID must be positive")
        if limit <= 0:
            raise ValidationException("Limit must be positive")
        if min_score < 0 or min_score > 1:
            raise ValidationException("Minimum score must be between 0 and 1")

        logger.info(
            "Getting similar movies",
            movie_id=movie_id,
            limit=limit,
            min_score=min_score,
            service="recommendation-api",
            component="recommendation_service",
            operation="get_similar_movies",
        )

        ***REMOVED*** First try the optimized path: get similar movies with metadata from vector DB
        try:
            start_time = time.time()
            similar_movies_with_metadata = (
                self.vector_service.find_similar_movies_by_id_with_metadata(
                    movie_id=movie_id,
                    limit=limit * 2,  ***REMOVED*** Get more to filter
                    min_score=min_score,
                )
            )

            ***REMOVED*** Check if we got results with v2 metadata (comprehensive data)
            if similar_movies_with_metadata:
                ***REMOVED*** Filter out any results with v1 metadata (legacy format)
                v2_results = [
                    (mid, score, metadata)
                    for mid, score, metadata in similar_movies_with_metadata
                    if metadata.get("metadata_version") == "v2"
                ]

                if v2_results:
                    vector_search_time = time.time() - start_time
                    logger.info(
                        f"Using optimized path: found {len(v2_results)} movies with comprehensive metadata in {vector_search_time:.3f}s"
                    )

                    ***REMOVED*** Get source movie title for reason (try from vector metadata first)
                    source_movie_title = "Unknown"
                    source_embedding = self.vector_service.get_movie_embedding(movie_id)
                    if source_embedding:
                        ***REMOVED*** Try to get source movie metadata from vector DB
                        try:
                            from recommendation_api.repositories.vector.client import (
                                get_qdrant_client,
                            )

                            client = get_qdrant_client()
                            source_point = client.get_point(point_id=movie_id, with_vectors=False)
                            if source_point and source_point.payload:
                                source_movie_title = source_point.payload.get("title", "Unknown")
                        except Exception as e:
                            logger.debug(f"Could not get source movie title from vector DB: {e}")

                    ***REMOVED*** If we couldn't get it from vector DB, try backend API as fallback
                    if source_movie_title == "Unknown":
                        source_movie = await self.movie_adapter.get_movie_by_id(movie_id)
                        if source_movie:
                            source_movie_title = source_movie.get("title", "Unknown")

                    ***REMOVED*** Filter movies by rating (metadata is already available)
                    filtered_movies = []
                    rejected_count = {"rating": 0, "missing_data": 0}

                    for movie_id_val, score, movie_metadata in v2_results:
                        ***REMOVED*** Apply filters
                        imdb_rating = movie_metadata.get("imdb_rating")

                        if min_rating is not None and (
                            imdb_rating is None or imdb_rating < min_rating
                        ):
                            rejected_count["rating"] += 1
                            logger.debug(
                                f"Movie {movie_id_val} rejected: rating {imdb_rating} < {min_rating}"
                            )
                            continue

                        logger.debug(f"Movie {movie_id_val} accepted: rating={imdb_rating}")
                        filtered_movies.append((movie_id_val, score, movie_metadata))

                        ***REMOVED*** Limit to requested number
                        if len(filtered_movies) >= limit:
                            break

                    logger.info(
                        f"Movie filtering results (optimized): {len(filtered_movies)} accepted, "
                        f"{rejected_count['rating']} rejected by rating, "
                        f"{rejected_count['missing_data']} missing data"
                    )

                    ***REMOVED*** Create recommendation objects with similarity scores
                    recommendations = []

                    for _movie_id_val, score, movie_metadata in filtered_movies:
                        reason = f"similar to {source_movie_title}"

                        ***REMOVED*** Convert metadata to recommendation using adapter's helper
                        recommendation = self.movie_adapter._convert_to_recommendation(
                            movie_metadata,
                            reason=reason,
                            score=score,
                        )
                        recommendations.append(recommendation)

                    total_time = time.time() - start_time
                    filters = {
                        "source_movie_id": movie_id,
                        "min_rating": min_rating,
                        "min_vote_count": min_vote_count,  ***REMOVED*** Keep for API compatibility
                        "min_score": min_score,
                        "limit": limit,
                        "optimized_path": True,  ***REMOVED*** Indicate we used the optimized path
                        "processing_time": f"{total_time:.3f}s",
                    }

                    logger.info(
                        f"Optimized path completed in {total_time:.3f}s (vs typical 4-5s for API path)"
                    )
                    return recommendations, filters

                else:
                    logger.info(
                        "Found results but all have legacy metadata format, falling back to API path"
                    )
            else:
                logger.info("No results from vector similarity search, falling back to API path")

        except Exception as e:
            logger.warning(
                f"Error in optimized similarity search path: {e}, falling back to API path"
            )

        ***REMOVED*** Fallback to original API-based approach
        logger.info("Using fallback path: querying vector service + backend API")

        ***REMOVED*** Get movie to use for recommendation reason (optional - may not exist in backend DB)
        source_movie = await self.movie_adapter.get_movie_by_id(movie_id)
        if not source_movie:
            logger.info(
                f"Source movie {movie_id} not found in backend DB, but continuing with vector similarity search"
            )

        ***REMOVED*** Get similar movies from vector service
        similar_movies = self.vector_service.find_similar_movies_by_id(
            movie_id=movie_id,
            limit=limit * 2,  ***REMOVED*** Get more to filter
            min_score=min_score,
        )

        if not similar_movies:
            logger.warning(f"No similar movies found for movie ID {movie_id}")
            return [], {"error": "No similar movies found"}

        ***REMOVED*** Get movie details for the IDs
        movie_ids = [movie_id for movie_id, _ in similar_movies]
        logger.debug(f"Fetching details for {len(movie_ids)} similar movies: {movie_ids[:10]}...")
        movies = await self.movie_adapter.get_movies_by_ids(movie_ids)
        logger.debug(
            f"Successfully retrieved {len(movies)} movie details out of {len(movie_ids)} requested"
        )

        ***REMOVED*** Create mapping of movie ID to similarity score
        similarity_scores = {movie_id: score for movie_id, score in similar_movies}

        ***REMOVED*** Filter movies by rating only (vote_count not available from backend API)
        filtered_movies = []
        rejected_count = {"rating": 0, "missing_data": 0}

        for movie_data in movies:
            movie_id_val = movie_data.get("id")
            if movie_id_val is None:
                rejected_count["missing_data"] += 1
                continue

            ***REMOVED*** Apply filters
            imdb_rating = movie_data.get("imdb_rating")

            if min_rating is not None and (imdb_rating is None or imdb_rating < min_rating):
                rejected_count["rating"] += 1
                logger.debug(f"Movie {movie_id_val} rejected: rating {imdb_rating} < {min_rating}")
                continue

            logger.debug(f"Movie {movie_id_val} accepted: rating={imdb_rating}")
            filtered_movies.append(movie_data)

            ***REMOVED*** Limit to requested number
            if len(filtered_movies) >= limit:
                break

        logger.info(
            f"Movie filtering results: {len(filtered_movies)} accepted, "
            f"{rejected_count['rating']} rejected by rating, "
            f"{rejected_count['missing_data']} missing data"
        )

        ***REMOVED*** Create recommendation objects with similarity scores and source movie
        recommendations = []

        for movie_data in filtered_movies:
            movie_id_val = movie_data.get("id")
            if movie_id_val is None:
                continue

            score = similarity_scores.get(movie_id_val, 0)
            reason = (
                f"similar to {source_movie.get('title', 'Unknown')}"
                if source_movie
                else f"similar to movie {movie_id}"
            )

            ***REMOVED*** Convert movie data to recommendation using adapter's helper
            recommendation = self.movie_adapter._convert_to_recommendation(
                movie_data,
                reason=reason,
                score=score,
            )
            recommendations.append(recommendation)

        filters = {
            "source_movie_id": movie_id,
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,  ***REMOVED*** Keep for API compatibility
            "min_score": min_score,
            "limit": limit,
        }

        return recommendations, filters

    async def generate_user_preference_vector(
        self,
        user_id: int,
        liked_movies: list[dict[str, Any]],
        watched_genres: dict[str, float],
    ) -> list[float]:
        """Generate a user preference vector using the ML API.

        Args:
            user_id: User ID
            liked_movies: List of movies liked by the user with ratings
            watched_genres: Genres watched by the user with preference weights

        Returns:
            User preference vector as list of floats
        """
        ***REMOVED*** Get ML API client
        ml_client = get_ml_api_client()

        ***REMOVED*** Generate preference vector
        return await ml_client.generate_user_preference_vector(
            user_id=str(user_id),
            liked_movies=liked_movies,
            watched_genres=watched_genres,
        )
