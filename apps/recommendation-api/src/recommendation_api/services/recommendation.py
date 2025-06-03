"""Recommendation service for the Recommendation API.

This module provides functionality for generating movie recommendations
based on various criteria and user preferences.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, Union
from sqlmodel import Session

from recommendation_api.db.operations import (
    get_trending_movies,
    get_popular_movies,
    get_movie_features,
    get_user_preference_movies,
    get_movies_by_ids,
    get_movie_by_id,
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

    def get_trending_recommendations(
        self,
        limit: int = 20,
        days: int = 7,
        min_rating: Optional[float] = None,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get trending movie recommendations.
        
        Args:
            limit: Maximum number of recommendations
            days: Number of days to look back for trending calculation
            min_rating: Minimum IMDb rating filter
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        movies = get_trending_movies(
            session=self.session,
            days=days,
            limit=limit,
            min_rating=min_rating,
        )
        
        recommendations = [
            MovieRecommendation.from_movie(movie, reason="trending")
            for movie in movies
        ]
        
        filters = {
            "days": days,
            "min_rating": min_rating,
            "limit": limit,
        }
        
        return recommendations, filters

    def get_popular_recommendations(
        self,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get popular movie recommendations.
        
        Args:
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count threshold
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        movies = get_popular_movies(
            session=self.session,
            limit=limit,
            min_rating=min_rating,
            min_vote_count=min_vote_count,
        )
        
        recommendations = [
            MovieRecommendation.from_movie(movie, reason="popular")
            for movie in movies
        ]
        
        filters = {
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
            "limit": limit,
        }
        
        return recommendations, filters

    def get_user_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        min_rating: float = 7.0,
        min_vote_count: int = 1000,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get personalized movie recommendations for a user.
        
        Args:
            user_id: User ID to get recommendations for
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count threshold
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        ***REMOVED*** Get user's liked movies
        liked_movies = get_user_preference_movies(
            session=self.session,
            user_id=user_id,
            preference_type="like",
        )
        
        if not liked_movies:
            ***REMOVED*** Fallback to popular recommendations if no liked movies
            return self.get_popular_recommendations(
                limit=limit,
                min_rating=min_rating,
                min_vote_count=min_vote_count,
            )
        
        ***REMOVED*** Create text representations of liked movies
        movie_texts = []
        for movie in liked_movies:
            if movie.id is None:
                continue
                
            features = get_movie_features(self.session, movie.id)
            if features:
                ***REMOVED*** Construct text representation
                text_parts = []
                
                if title := features.get("title"):
                    text_parts.append(f"Title: {title}")
                
                if overview := features.get("overview"):
                    ***REMOVED*** Truncate overview to avoid token limits
                    overview_truncated = overview[:500] if len(overview) > 500 else overview
                    text_parts.append(f"Plot: {overview_truncated}")
                
                if genres := features.get("genres"):
                    if isinstance(genres, list) and genres:
                        genres_str = ", ".join(genres)
                        text_parts.append(f"Genres: {genres_str}")
                
                if cast := features.get("cast"):
                    if isinstance(cast, list) and cast:
                        ***REMOVED*** Use top 3 cast members
                        cast_str = ", ".join(cast[:3])
                        text_parts.append(f"Starring: {cast_str}")
                
                if director := features.get("director"):
                    text_parts.append(f"Directed by: {director}")
                
                if release_year := features.get("release_year"):
                    text_parts.append(f"Released: {release_year}")
                
                ***REMOVED*** Join all parts with periods
                movie_text = ". ".join(text_parts)
                movie_texts.append(movie_text)
        
        if not movie_texts:
            ***REMOVED*** Fallback to popular recommendations if no text representations
            return self.get_popular_recommendations(
                limit=limit,
                min_rating=min_rating,
                min_vote_count=min_vote_count,
            )
        
        ***REMOVED*** Generate user preference vector
        user_vector = generate_user_preference_vector(movie_texts)
        
        ***REMOVED*** Get user's watched movies to exclude
        watched_movies = get_user_preference_movies(
            session=self.session,
            user_id=user_id,
            preference_type="watched",
        )
        exclude_ids = [m.id for m in watched_movies if m.id is not None]
        
        ***REMOVED*** Search for similar movies using vector service
        similar_movies = self.vector_service.find_similar_movies(
            query_embedding=user_vector,
            limit=limit,
            min_score=0.6,
            exclude_movie_ids=exclude_ids,
        )
        
        ***REMOVED*** Get full movie details
        movie_ids = [movie_id for movie_id, _ in similar_movies]
        movies = get_movies_by_ids(self.session, movie_ids)
        
        ***REMOVED*** Create recommendations
        recommendations = []
        for movie in movies:
            ***REMOVED*** Find the score for this movie
            score = next((score for mid, score in similar_movies if mid == movie.id), None)
            recommendations.append(
                MovieRecommendation.from_movie(movie, reason="personalized", score=score)
            )
        
        filters = {
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
            "limit": limit,
            "excluded_watched": len(exclude_ids),
        }
        
        return recommendations, filters

    def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 20,
        min_rating: float = 6.0,
        min_vote_count: int = 500,
        min_score: float = 0.01,
    ) -> Tuple[List[MovieRecommendation], Dict[str, Any]]:
        """Get movies similar to a given movie.
        
        Args:
            movie_id: ID of the movie to find similar movies for
            limit: Maximum number of recommendations
            min_rating: Minimum IMDb rating
            min_vote_count: Minimum vote count threshold
            min_score: Minimum similarity score (0-1) for vector search
            
        Returns:
            Tuple of (recommendations list, filters dict)
        """
        ***REMOVED*** Check if movie exists
        movie = get_movie_by_id(self.session, movie_id)
        if not movie:
            return [], {
                "min_rating": min_rating,
                "min_vote_count": min_vote_count,
                "limit": limit,
                "min_score": min_score,
                "error": f"Movie with ID {movie_id} not found",
            }
            
        ***REMOVED*** Search for similar movies using vector service
        ***REMOVED*** The vector service now handles fallbacks internally
        similar_movies = self.vector_service.find_similar_movies_by_id(
            movie_id=movie_id,
            limit=limit,
            min_score=min_score,
        )
        
        if not similar_movies:
            return [], {
                "min_rating": min_rating,
                "min_vote_count": min_vote_count,
                "limit": limit,
                "min_score": min_score,
                "error": "No similar movies found",
            }
        
        ***REMOVED*** Get full movie details
        movie_ids = [movie_id for movie_id, _ in similar_movies]
        movies = get_movies_by_ids(self.session, movie_ids)
        
        ***REMOVED*** Filter movies by rating and vote count
        filtered_movies = []
        for movie in movies:
            if movie.imdb_rating is None or movie.imdb_rating < min_rating:
                continue
            if movie.vote_count is None or movie.vote_count < min_vote_count:
                continue
            filtered_movies.append(movie)
        
        ***REMOVED*** Create recommendations
        recommendations = []
        for movie in filtered_movies:
            ***REMOVED*** Find the score for this movie
            score = next((score for mid, score in similar_movies if mid == movie.id), None)
            recommendations.append(
                MovieRecommendation.from_movie(movie, reason="similar", score=score)
            )
        
        filters = {
            "min_rating": min_rating,
            "min_vote_count": min_vote_count,
            "limit": limit,
            "min_score": min_score,
            "total_found": len(similar_movies),
            "filtered_out": len(similar_movies) - len(filtered_movies),
        }
        
        return recommendations, filters 