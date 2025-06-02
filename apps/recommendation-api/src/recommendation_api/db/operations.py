"""Database operations for the Recommendation API service."""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlmodel import Session, select, and_, or_, func, col

***REMOVED*** Import models from the shared movie-storage library
from movie_storage.models.movie import Movie
from movie_storage.models.user import User
from movie_storage.models.user_interaction import UserMovieInteraction
from movie_storage.models.genre import Genre
from movie_storage.models.credit import Credit

from recommendation_api.config import settings

logger = logging.getLogger(__name__)


def get_movies_for_embeddings(
    session: Session,
    limit: Optional[int] = None,
    offset: int = 0,
    min_rating: Optional[float] = None,
) -> List[Movie]:
    """Get movies that need embeddings or embedding updates.
    
    Args:
        session: Database session
        limit: Maximum number of movies to return
        offset: Number of movies to skip
        min_rating: Minimum IMDb rating filter
        
    Returns:
        List of Movie objects
    """
    query = select(Movie).where(Movie.title != "")
    
    ***REMOVED*** Filter by minimum rating if specified
    if min_rating is not None:
        query = query.where(
            and_(
                col(Movie.imdb_rating).isnot(None),
                col(Movie.imdb_rating) >= min_rating
            )
        )
    
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
    
    ***REMOVED*** Get genres
    genres = [genre.name for genre in movie.genres] if movie.genres else []
    
    ***REMOVED*** Get top cast members (limit to top 5 for embedding)
    cast_query = select(Credit).where(
        and_(
            Credit.movie_id == movie_id,
            Credit.department == "Acting"
        )
    ).limit(5)
    
    cast_members = [credit.name for credit in session.exec(cast_query).all()]
    
    ***REMOVED*** Get director
    director_query = select(Credit).where(
        and_(
            Credit.movie_id == movie_id,
            Credit.department == "Directing",
            Credit.job == "Director"
        )
    )
    
    director_credit = session.exec(director_query).first()
    director = director_credit.name if director_credit else None
    
    features = {
        "id": movie.id,
        "title": movie.title,
        "original_title": movie.original_title,
        "overview": movie.overview,
        "genres": genres,
        "cast": cast_members,
        "director": director,
        "release_year": movie.release_date.year if movie.release_date else None,
        "imdb_rating": movie.imdb_rating,
        "tmdb_rating": movie.tmdb_rating,
        "language": movie.language,
    }
    
    return features


def get_user_movie_interactions(
    session: Session,
    user_id: int,
    interaction_types: Optional[List[str]] = None,
) -> List[UserMovieInteraction]:
    """Get user's movie interactions for recommendation generation.
    
    Args:
        session: Database session
        user_id: User ID
        interaction_types: List of interaction types to filter by
        
    Returns:
        List of UserMovieInteraction objects
    """
    query = select(UserMovieInteraction).where(
        UserMovieInteraction.user_id == user_id
    )
    
    ***REMOVED*** Filter by interaction types if specified
    if interaction_types:
        filters = []
        if "watched" in interaction_types:
            filters.append(UserMovieInteraction.watched == True)
        if "liked" in interaction_types:
            filters.append(UserMovieInteraction.liked == True)
        if "watchlist" in interaction_types:
            filters.append(UserMovieInteraction.in_watchlist == True)
        
        if filters:
            query = query.where(or_(*filters))
    
    interactions = list(session.exec(query).all())
    logger.info(f"Retrieved {len(interactions)} interactions for user {user_id}")
    return interactions


def get_trending_movies(
    session: Session,
    days: int = 7,
    limit: int = 20,
    min_rating: Optional[float] = None,
) -> List[Movie]:
    """Get trending movies based on recent user interactions.
    
    Args:
        session: Database session
        days: Number of days to look back for trending calculation
        limit: Maximum number of movies to return
        min_rating: Minimum IMDb rating filter
        
    Returns:
        List of trending Movie objects
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    ***REMOVED*** Get movies with recent interactions (simplified approach)
    interaction_query = select(UserMovieInteraction.movie_id).where(
        UserMovieInteraction.created_at >= cutoff_date
    ).distinct()
    
    movie_ids = [row for row in session.exec(interaction_query).all()]
    
    if not movie_ids:
        ***REMOVED*** Fallback to popular movies if no recent interactions
        return get_popular_movies(session, limit=limit, min_rating=min_rating or 6.0)
    
    query = select(Movie).where(col(Movie.id).in_(movie_ids))
    
    ***REMOVED*** Apply rating filter if specified
    if min_rating is not None:
        query = query.where(
            and_(
                col(Movie.imdb_rating).isnot(None),
                col(Movie.imdb_rating) >= min_rating
            )
        )
    
    movies = list(session.exec(query.limit(limit)).all())
    logger.info(f"Retrieved {len(movies)} trending movies")
    return movies


def get_popular_movies(
    session: Session,
    limit: int = 20,
    min_rating: float = 7.0,
    min_vote_count: int = 1000,
) -> List[Movie]:
    """Get popular movies based on ratings and vote counts.
    
    Args:
        session: Database session
        limit: Maximum number of movies to return
        min_rating: Minimum IMDb rating
        min_vote_count: Minimum vote count
        
    Returns:
        List of popular Movie objects
    """
    query = select(Movie).where(
        and_(
            col(Movie.imdb_rating).isnot(None),
            col(Movie.imdb_rating) >= min_rating,
            col(Movie.vote_count).isnot(None),
            col(Movie.vote_count) >= min_vote_count
        )
    ).order_by(col(Movie.id))  ***REMOVED*** Simple ordering for now
    
    movies = list(session.exec(query.limit(limit)).all())
    logger.info(f"Retrieved {len(movies)} popular movies")
    return movies


def create_movie_similarity(
    session: Session,
    movie_id_1: int,
    movie_id_2: int,
    similarity_score: float,
) -> bool:
    """Create or update a movie similarity record.
    
    Args:
        session: Database session
        movie_id_1: First movie ID
        movie_id_2: Second movie ID
        similarity_score: Similarity score between movies
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ***REMOVED*** Note: This would require a MovieSimilarity model to be created
        ***REMOVED*** For now, we'll log the operation
        logger.info(
            f"Would create similarity: {movie_id_1} <-> {movie_id_2} "
            f"(score: {similarity_score:.3f})"
        )
        return True
    except Exception as e:
        logger.error(f"Error creating movie similarity: {e}")
        return False


def get_movie_similarities(
    session: Session,
    movie_id: int,
    limit: int = 10,
    min_score: float = 0.7,
) -> List[Tuple[int, float]]:
    """Get similar movies for a given movie.
    
    Args:
        session: Database session
        movie_id: Movie ID to find similarities for
        limit: Maximum number of similar movies to return
        min_score: Minimum similarity score
        
    Returns:
        List of tuples (movie_id, similarity_score)
    """
    ***REMOVED*** Note: This would require a MovieSimilarity model to be implemented
    ***REMOVED*** For now, return empty list
    logger.info(f"Would retrieve similarities for movie {movie_id}")
    return []


def get_movies_by_ids(session: Session, movie_ids: List[int]) -> List[Movie]:
    """Get movies by their IDs.
    
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
    logger.info(f"Retrieved {len(movies)} movies by IDs")
    return movies


def get_user_preference_movies(
    session: Session,
    user_id: int,
    preference_type: str = "liked",
    limit: Optional[int] = None,
) -> List[Movie]:
    """Get movies based on user preferences (liked, watched, etc.).
    
    Args:
        session: Database session
        user_id: User ID
        preference_type: Type of preference ("liked", "watched", "watchlist")
        limit: Maximum number of movies to return
        
    Returns:
        List of Movie objects
    """
    query = (
        select(Movie)
        .join(UserMovieInteraction, onclause=col(Movie.id) == col(UserMovieInteraction.movie_id))
        .where(UserMovieInteraction.user_id == user_id)
    )
    
    ***REMOVED*** Filter by preference type
    if preference_type == "liked":
        query = query.where(UserMovieInteraction.liked == True)
    elif preference_type == "watched":
        query = query.where(UserMovieInteraction.watched == True)
    elif preference_type == "watchlist":
        query = query.where(UserMovieInteraction.in_watchlist == True)
    
    if limit is not None:
        query = query.limit(limit)
    
    movies = list(session.exec(query).all())
    logger.info(f"Retrieved {len(movies)} {preference_type} movies for user {user_id}")
    return movies 