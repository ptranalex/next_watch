"""Database operations for the Recommendation API service."""

import logging
import random
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlmodel import Session, select, and_, or_, func, col

***REMOVED*** Import models from the shared movie-storage library
from movie_storage.models.movie import Movie
***REMOVED*** Comment out imports that might be causing issues
***REMOVED*** from movie_storage.models.user_interaction import UserMovieInteraction
***REMOVED*** from movie_storage.models.genre import Genre
***REMOVED*** from movie_storage.models.credit import Credit

from recommendation_api.config import settings

logger = logging.getLogger(__name__)


def get_movies_for_embeddings(
    session: Session,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Movie]:
    """Get movies that need embeddings or embedding updates.
    
    Args:
        session: Database session
        limit: Maximum number of movies to return
        offset: Number of movies to skip
        
    Returns:
        List of Movie objects
    """
    query = select(Movie).where(Movie.title != "")
    
    ***REMOVED*** Order by ID for consistent results
    query = query.order_by(col(Movie.id))
    
    if offset > 0:
        query = query.offset(offset)
    
    if limit is not None:
        query = query.limit(limit)
    
    movies = list(session.exec(query).all())
    logger.info(f"Retrieved {len(movies)} movies for embeddings")
    return movies


def get_movie_features(session: Session, movie_id: int) -> Optional[Dict[str, Any]]:
    """Get movie features for embedding generation.
    
    Args:
        session: Database session
        movie_id: Movie ID
        
    Returns:
        Dictionary with movie features or None if not found
    """
    movie = session.get(Movie, movie_id)
    if not movie:
        return None
    
    ***REMOVED*** Simplified version without related entities
    features = {
        "id": movie.id,
        "title": movie.title,
        "original_title": movie.original_title,
        "overview": movie.overview,
        "release_year": movie.release_date.year if movie.release_date else None,
        "imdb_rating": movie.imdb_rating,
        "tmdb_rating": movie.tmdb_rating,
        "language": movie.language,
    }
    
    return features


def get_popular_movies_direct(
    session: Session,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
) -> List[Movie]:
    """Get popular movies directly from the database.
    
    This is a simplified version of the get_popular_movies function
    that doesn't rely on other models like UserMovieInteraction.
    
    Args:
        session: Database session
        limit: Maximum number of movies to return
        min_rating: Minimum IMDb rating
        min_vote_count: Minimum vote count threshold
        
    Returns:
        List of Movie objects
    """
    query = select(Movie).where(
        (col(Movie.imdb_rating) >= min_rating) &
        (col(Movie.vote_count) >= min_vote_count)
    )
    
    ***REMOVED*** Order by rating and vote count for popularity
    query = query.order_by(
        col(Movie.imdb_rating).desc(),
        col(Movie.vote_count).desc()
    )
    
    ***REMOVED*** Limit results
    query = query.limit(limit)
    
    ***REMOVED*** Execute query
    movies = list(session.exec(query).all())
    logger.info(f"Retrieved {len(movies)} popular movies")
    return movies


def get_personalized_recommendations_direct(
    session: Session,
    user_id: int,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
) -> List[Movie]:
    """Get personalized movie recommendations for a user.
    
    This is a simplified placeholder implementation that simulates personalized recommendations
    by combining popular movies with some random selections to add variety.
    In a real implementation, this would use user interaction data and a recommendation algorithm.
    
    Args:
        session: Database session
        user_id: User ID
        limit: Maximum number of movies to return
        min_rating: Minimum IMDb rating
        min_vote_count: Minimum vote count threshold
        
    Returns:
        List of Movie objects
    """
    ***REMOVED*** Get popular movies as a base
    popular_count = max(1, int(limit * 0.7))  ***REMOVED*** 70% popular
    popular_movies = get_popular_movies_direct(
        session, 
        limit=popular_count,
        min_rating=min_rating,
        min_vote_count=min_vote_count
    )
    
    ***REMOVED*** Get some more random highly-rated movies for variety
    ***REMOVED*** These might be less known movies with good ratings
    discover_count = limit - len(popular_movies)
    if discover_count > 0:
        ***REMOVED*** Find movies with good ratings but not necessarily high vote counts
        ***REMOVED*** This simulates "discovery" recommendations
        discover_query = select(Movie).where(
            (col(Movie.imdb_rating) >= min_rating) &
            (col(Movie.vote_count) >= min_vote_count // 2)  ***REMOVED*** Lower vote count threshold
        )
        
        ***REMOVED*** Add a bit of randomness to the order
        discover_query = discover_query.order_by(func.random())
        discover_query = discover_query.limit(discover_count * 2)  ***REMOVED*** Get more, then filter
        
        discover_movies = list(session.exec(discover_query).all())
        
        ***REMOVED*** Get IDs of popular movies to avoid duplicates
        popular_ids = {movie.id for movie in popular_movies if movie.id is not None}
        
        ***REMOVED*** Filter out movies already in popular_movies
        unique_discover_movies = [
            movie for movie in discover_movies
            if movie.id is not None and movie.id not in popular_ids
        ]
        
        ***REMOVED*** Take up to discover_count movies
        discover_movies = unique_discover_movies[:discover_count]
        
        ***REMOVED*** Combine popular and discover movies
        all_movies = popular_movies + discover_movies
    else:
        all_movies = popular_movies
    
    ***REMOVED*** Shuffle the order slightly to make it less predictable
    ***REMOVED*** We're keeping some of the popular movies at the top for quality
    top_picks = all_movies[:min(5, len(all_movies))]
    remaining = all_movies[min(5, len(all_movies)):]
    random.shuffle(remaining)
    
    ***REMOVED*** Return the combined list
    result = top_picks + remaining
    logger.info(f"Generated {len(result)} personalized recommendations for user {user_id}")
    return result


***REMOVED*** Comment out functions that use the commented-out models
"""
def get_user_movie_interactions(
    session: Session,
    user_id: int,
    interaction_types: Optional[List[str]] = None,
) -> List[UserMovieInteraction]:
    ***REMOVED*** ...
"""

"""
def get_trending_movies(
    session: Session,
    days: int = 7,
    limit: int = 20,
    min_rating: Optional[float] = None,
) -> List[Movie]:
    ***REMOVED*** ...
"""

"""
def get_popular_movies(
    session: Session,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
) -> List[Movie]:
    ***REMOVED*** ...
"""

"""
def create_movie_similarity(
    session: Session,
    movie_id_1: int,
    movie_id_2: int,
    similarity_score: float,
) -> bool:
    ***REMOVED*** ...
"""

"""
def get_similar_movies(
    session: Session,
    movie_id: int,
    limit: int = 10,
    min_score: float = 0.7,
) -> List[Tuple[int, float]]:
    ***REMOVED*** ...
"""

def get_movies_by_ids(session: Session, movie_ids: List[int]) -> List[Movie]:
    """Get movies by IDs.
    
    Args:
        session: Database session
        movie_ids: List of movie IDs
        
    Returns:
        List of Movie objects
    """
    if not movie_ids:
        return []
    
    query = select(Movie).where(col(Movie.id).in_(movie_ids))
    movies = list(session.exec(query).all())
    return movies


def get_movie_by_id(session: Session, movie_id: int) -> Optional[Movie]:
    """Get movie by ID.
    
    Args:
        session: Database session
        movie_id: Movie ID
        
    Returns:
        Movie object or None if not found
    """
    return session.get(Movie, movie_id)


***REMOVED*** Comment out functions that use the commented-out models
"""
def get_user_preference_movies(
    session: Session,
    user_id: int,
    preference_type: str = "liked",
    limit: Optional[int] = None,
) -> List[Movie]:
    ***REMOVED*** ...
"""

def get_all_movie_ids(session: Session) -> List[int]:
    """Get all movie IDs from the database.
    
    Args:
        session: Database session
        
    Returns:
        List of movie IDs
    """
    query = select(Movie.id).where(Movie.id != None)
    result = session.exec(query).all()
    
    ***REMOVED*** Convert to list of integers and filter out None values
    movie_ids = [movie_id for movie_id in result if movie_id is not None]
    
    logger.info(f"Retrieved {len(movie_ids)} movie IDs from database")
    return movie_ids 