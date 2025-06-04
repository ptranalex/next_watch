"""Recommendation service for the Recommendation API.

This module provides functionality for generating movie recommendations
based on various criteria and user preferences.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, Union
from sqlmodel import Session

from recommendation_api.db.operations import (
    ***REMOVED*** Comment out unavailable functions
    ***REMOVED*** get_trending_movies,
    ***REMOVED*** get_popular_movies,
    get_movie_features,
    ***REMOVED*** get_user_preference_movies,
    get_movies_by_ids,
    get_movie_by_id,
    get_popular_movies_direct,
    get_personalized_recommendations_direct,
)
from recommendation_api.services.vector_service import VectorService, get_vector_service
from recommendation_api.services.embedding import generate_user_preference_vector
from movie_storage.models.movie import Movie
from recommendation_api.models.recommendation import MovieRecommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating movie recommendations."""

    def __init__(self, session: Session, vector_service: Optional[VectorService] = None):
        """Initialize the recommendation service.
        
        Args:
            session: Database session
            vector_service: Vector service for similarity searches
        """
        self.session = session
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

    def get_popular_recommendations_direct(
        self,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get popular movie recommendations using the direct database query.
        
        This is a replacement for get_popular_recommendations that uses
        the simplified get_popular_movies_direct function.
        
        Args:
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating threshold
            min_vote_count: Minimum vote count threshold
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        ***REMOVED*** Get popular movies from database
        movies = get_popular_movies_direct(
            self.session,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )
        
        ***REMOVED*** Convert to recommendations
        recommendations = []
        for movie in movies:
            recommendation = MovieRecommendation.from_movie(
                movie,
                reason="popular movie with high ratings",
                score=float(movie.imdb_rating) if movie.imdb_rating else 0.0,
            )
            recommendations.append(recommendation)
        
        ***REMOVED*** Create filters dictionary for response
        filters = {
            "limit": limit,
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
        }
        
        return recommendations, filters

    def get_user_recommendations_direct(
        self,
        user_id: int,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get personalized movie recommendations using the direct database query.
        
        This is a replacement for get_user_recommendations that uses
        the simplified get_personalized_recommendations_direct function.
        
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
            
        ***REMOVED*** Get personalized recommendations from database
        movies = get_personalized_recommendations_direct(
            self.session,
            user_id=user_id,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )
        
        ***REMOVED*** Convert to recommendations
        recommendations = []
        for movie in movies:
            ***REMOVED*** Add a personalized reason
            reason = "recommended for you based on your preferences"
            
            ***REMOVED*** Use rating as a base score, and add some randomness for variety
            base_score = float(movie.imdb_rating) / 10.0 if movie.imdb_rating else 0.5
            
            recommendation = MovieRecommendation.from_movie(
                movie,
                reason=reason,
                score=base_score,
            )
            recommendations.append(recommendation)
        
        ***REMOVED*** Create filters dictionary for response
        filters = {
            "user_id": user_id,
            "limit": limit,
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
        }
        
        return recommendations, filters

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

    ***REMOVED*** Keep this method as it only uses get_movie_features and vector_service
    def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20,
        min_rating: float = 6.0,
        min_vote_count: int = 500,
        min_score: float = 0.01,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get similar movies based on vector similarity.
        
        Args:
            movie_id: Movie ID to find similar movies for
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count threshold
            min_score: Minimum similarity score
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        ***REMOVED*** Get movie features
        features = get_movie_features(self.session, movie_id)
        if not features:
            logger.warning(f"No features found for movie ID {movie_id}")
            return [], {"error": "Movie not found"}
        
        ***REMOVED*** Get movie to use for recommendation reason
        source_movie = get_movie_by_id(self.session, movie_id)
        if not source_movie:
            logger.warning(f"Movie with ID {movie_id} not found")
            return [], {"error": "Movie not found"}
        
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
        movies = get_movies_by_ids(self.session, movie_ids)
        
        ***REMOVED*** Create mapping of movie ID to similarity score
        similarity_scores = {movie_id: score for movie_id, score in similar_movies}
        
        ***REMOVED*** Filter movies by rating and vote count if specified
        filtered_movies = []
        for movie in movies:
            if movie.id is None:
                continue
                
            ***REMOVED*** Apply filters
            if min_rating is not None and (movie.imdb_rating is None or movie.imdb_rating < min_rating):
                continue
                
            if min_vote_count is not None and (movie.vote_count is None or movie.vote_count < min_vote_count):
                continue
                
            filtered_movies.append(movie)
            
            ***REMOVED*** Limit to requested number
            if len(filtered_movies) >= limit:
                break
        
        ***REMOVED*** Create recommendation objects with similarity scores and source movie
        recommendations = []
        for movie in filtered_movies:
            if movie.id is None:
                continue
                
            score = similarity_scores.get(movie.id, 0)
            reason = f"similar to {source_movie.title}" if source_movie else "similar"
            
            recommendation = MovieRecommendation.from_movie(
                movie,
                reason=reason,
                score=score,
            )
            recommendations.append(recommendation)
        
        filters = {
            "source_movie_id": movie_id,
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
            "min_score": min_score,
            "limit": limit,
        }
        
        return recommendations, filters 