"""
User movie interactions API routes.

These routes handle user interactions with movies, like marking movies as watched,
adding them to watchlists, or liking them.
"""

from typing import Annotated, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, Field

from backend_api.db.database import get_db
from backend_api.routes.v1.auth import get_current_user
from backend_api.schemas.user_interaction_schema import (
    UserMovieInteractionResponse,
    UserMovieInteractionWithMovie,
    MovieSummary,
    UserMovieDetail,
)
from backend_api.services.user_interaction import UserInteractionService
from backend_api.queries.user_interaction_query import UserInteractionQuery
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from movie_storage.models.user import User
from movie_storage.models.movie import Movie
from movie_storage.models.user_interaction import UserMovieInteraction
from movie_storage.db.operations import get_movie_by_id

***REMOVED*** Create router
router = APIRouter(prefix="/user/movies", tags=["user-movies"])


***REMOVED*** Get dependencies
def get_user_interaction_service():
    """Get user interaction service."""
    return UserInteractionService()


def get_user_interaction_query():
    """Get user interaction query."""
    return UserInteractionQuery()


***REMOVED*** Get user interaction with a specific movie
@router.get(
    "/{movie_id}/interaction",
    response_model=Optional[UserMovieInteractionResponse],
    summary="Get user interaction with a specific movie",
)
async def get_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
):
    """
    Get the current user's interaction with a specific movie.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query

    Returns:
        User's interaction with the movie, or None if no interaction exists
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interaction
    try:
        return interaction_query.get_user_interaction(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watchlist
@router.get(
    "/watchlist",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's watchlist",
)
async def get_user_watchlist_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's watchlist.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies in the user's watchlist
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watchlist(
            db, current_user.id, limit, offset
        )
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watched movies
@router.get(
    "/watched",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's watched movies",
)
async def get_user_watched_movies_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's watched movies.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has watched
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_watched_movies(
            db, current_user.id, limit, offset
        )
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user liked movies
@router.get(
    "/liked",
    response_model=List[UserMovieInteractionResponse],
    summary="Get user's liked movies",
)
async def get_user_liked_movies_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's liked movies.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has liked
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Get user interactions
    try:
        interactions, _ = interaction_query.get_user_liked_movies(
            db, current_user.id, limit, offset
        )
        return interactions
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie in watchlist
@router.post(
    "/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie in watchlist",
)
async def toggle_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
    """
    Toggle a movie in the user's watchlist.

    If the movie is not in the watchlist, it will be added.
    If the movie is already in the watchlist, it will be removed.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle watchlist status
    try:
        return interaction_service.toggle_watchlist(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie as watched
@router.post(
    "/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie as watched",
)
async def toggle_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
    """
    Toggle a movie as watched.

    If the movie is not marked as watched, it will be marked as watched.
    If the movie is already marked as watched, it will be unmarked.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle watched status
    try:
        return interaction_service.toggle_watched(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Toggle movie as liked
@router.post(
    "/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Toggle movie as liked",
)
async def toggle_liked(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
    """
    Toggle a movie as liked.

    If the movie is not liked, it will be marked as liked.
    If the movie is already liked, it will be unmarked.

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        Updated user interaction

    Raises:
        HTTPException: If the movie doesn't exist
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Toggle liked status
    try:
        return interaction_service.toggle_liked(db, current_user.id, movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Delete a movie interaction completely
@router.delete(
    "/{movie_id}/interaction",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie interaction",
)
async def delete_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[
        UserInteractionService, Depends(get_user_interaction_service)
    ],
):
    """
    Delete a user's interaction with a movie completely.

    This removes all interaction flags (watched, liked, in_watchlist).

    Args:
        movie_id: Movie ID
        current_user: Current authenticated user
        db: Database session
        interaction_service: User interaction service

    Returns:
        No content

    Raises:
        HTTPException: If the movie doesn't exist or has no interaction
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    ***REMOVED*** Delete interaction
    try:
        success = interaction_service.delete_interaction(db, current_user.id, movie_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watchlist with movie details
@router.get(
    "/watchlist/details",
    response_model=List[UserMovieInteractionWithMovie],
    summary="Get user's watchlist with movie details",
)
async def get_user_watchlist_with_details(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's watchlist with full movie details included.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies in the user's watchlist with details
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Get user interactions with pagination
        interactions, _ = interaction_query.get_user_watchlist(
            db, current_user.id, limit=0, offset=0
        )

        ***REMOVED*** Get detailed interactions with movies
        detailed_interactions, _ = interaction_query.get_user_interactions_with_movies(
            db, current_user.id, interactions, limit, offset
        )

        ***REMOVED*** Create response objects
        result = []
        for item in detailed_interactions:
            interaction = item["interaction"]
            movie = item["movie"]

            ***REMOVED*** Create response objects from models
            interaction_response = UserMovieInteractionResponse(
                id=interaction.id,
                user_id=interaction.user_id,
                movie_id=interaction.movie_id,
                watched=interaction.watched,
                liked=interaction.liked,
                in_watchlist=interaction.in_watchlist,
                created_at=interaction.created_at,
                updated_at=interaction.updated_at,
            )

            movie_summary = MovieSummary(
                id=movie.id,
                title=movie.title,
                poster_url=movie.poster_url,
                release_date=movie.release_date,
                tmdb_rating=movie.tmdb_rating,
            )

            result.append(
                UserMovieInteractionWithMovie(
                    interaction=interaction_response, movie=movie_summary
                )
            )

        return result
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user watched movies with details
@router.get(
    "/watched/details",
    response_model=List[UserMovieInteractionWithMovie],
    summary="Get user's watched movies with details",
)
async def get_user_watched_movies_with_details(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's watched movies with full movie details included.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has watched with details
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Get user interactions
        interactions, _ = interaction_query.get_user_watched_movies(
            db, current_user.id, limit=0, offset=0
        )

        ***REMOVED*** Get detailed interactions with movies
        detailed_interactions, _ = interaction_query.get_user_interactions_with_movies(
            db, current_user.id, interactions, limit, offset
        )

        ***REMOVED*** Create response objects
        result = []
        for item in detailed_interactions:
            interaction = item["interaction"]
            movie = item["movie"]

            ***REMOVED*** Create response objects from models
            interaction_response = UserMovieInteractionResponse(
                id=interaction.id,
                user_id=interaction.user_id,
                movie_id=interaction.movie_id,
                watched=interaction.watched,
                liked=interaction.liked,
                in_watchlist=interaction.in_watchlist,
                created_at=interaction.created_at,
                updated_at=interaction.updated_at,
            )

            movie_summary = MovieSummary(
                id=movie.id,
                title=movie.title,
                poster_url=movie.poster_url,
                release_date=movie.release_date,
                tmdb_rating=movie.tmdb_rating,
            )

            result.append(
                UserMovieInteractionWithMovie(
                    interaction=interaction_response, movie=movie_summary
                )
            )

        return result
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** Get user liked movies with details
@router.get(
    "/liked/details",
    response_model=List[UserMovieInteractionWithMovie],
    summary="Get user's liked movies with details",
)
async def get_user_liked_movies_with_details(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's liked movies with full movie details included.

    Args:
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movies the user has liked with details
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Get user interactions
        interactions, _ = interaction_query.get_user_liked_movies(
            db, current_user.id, limit=0, offset=0
        )

        ***REMOVED*** Get detailed interactions with movies
        detailed_interactions, _ = interaction_query.get_user_interactions_with_movies(
            db, current_user.id, interactions, limit, offset
        )

        ***REMOVED*** Create response objects
        result = []
        for item in detailed_interactions:
            interaction = item["interaction"]
            movie = item["movie"]

            ***REMOVED*** Create response objects from models
            interaction_response = UserMovieInteractionResponse(
                id=interaction.id,
                user_id=interaction.user_id,
                movie_id=interaction.movie_id,
                watched=interaction.watched,
                liked=interaction.liked,
                in_watchlist=interaction.in_watchlist,
                created_at=interaction.created_at,
                updated_at=interaction.updated_at,
            )

            movie_summary = MovieSummary(
                id=movie.id,
                title=movie.title,
                poster_url=movie.poster_url,
                release_date=movie.release_date,
                tmdb_rating=movie.tmdb_rating,
            )

            result.append(
                UserMovieInteractionWithMovie(
                    interaction=interaction_response, movie=movie_summary
                )
            )

        return result
    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** New optimized endpoint for movie details by category
@router.get(
    "/{category}/movie-details",
    response_model=List[UserMovieDetail],
    summary="Get user's movies with optimized details",
)
async def get_user_movie_details(
    category: Annotated[
        str, Path(title="Category", description="One of: watchlist, watched, liked")
    ],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[
        UserInteractionQuery, Depends(get_user_interaction_query)
    ],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """
    Get the current user's movie details for a specific category using an optimized query.

    This endpoint uses a more efficient database query than the /details endpoints
    by retrieving movie data and interaction status in a single operation.

    Args:
        category: Category of movies to retrieve (watchlist, watched, liked)
        current_user: Current authenticated user
        db: Database session
        interaction_query: User interaction query
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        List of movie details with interaction status
    """
    ***REMOVED*** Ensure user ID is available
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is missing",
        )

    try:
        ***REMOVED*** Get movie details with optimized query
        movie_details, _ = interaction_query.get_user_movie_details(
            db, current_user.id, category, limit, offset
        )
        return movie_details
    except ValidationError as e:
        raise service_error_to_http_exception(e)
