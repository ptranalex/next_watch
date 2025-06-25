"""
User collection routes for the backend API - Collection-Oriented Design.

These routes handle user collections as first-class resources:
- Watchlist collection
- Watched movies collection
- Liked movies collection

Following REST best practices with proper HTTP semantics and status codes.
Now using fast-core ResponseBuilder for consistent response format across the monorepo.
"""

from datetime import datetime
from typing import Annotated, List, Union, Dict, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

***REMOVED*** Import fast-core dependencies and utilities
from fast_core.dependencies import get_request_id
from fast_core.responses import ResponseBuilder, PaginatedResponse, ActionResponse

from config.logging import get_logger
from backend_api.db.database import get_db
from backend_api.dependencies import get_user_id_from_header
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from backend_api.queries import UserInteractionQuery
from backend_api.schemas import (
    AddToCollectionRequest,
    CollectionItemResponse,
    CollectionOperationResponse,
    UserMovieInteractionResponse,
)
from backend_api.models.user_interaction import UserMovieInteraction
from backend_api.services.user_interaction import UserInteractionService

logger = get_logger(__name__)

***REMOVED*** Create router with prefix for user collections
router = APIRouter(prefix="/user", tags=["user-collections"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)


***REMOVED*** Get dependencies
def get_user_interaction_service() -> UserInteractionService:
    """Get user interaction service."""
    return UserInteractionService()


def get_user_interaction_query() -> UserInteractionQuery:
    """Get user interaction query."""
    return UserInteractionQuery()


***REMOVED*** ============================================================================
***REMOVED*** SINGLE INTERACTION ENDPOINT
***REMOVED*** ============================================================================


@router.get(
    "/interactions/movies/{movie_id}",
    response_model=Union[UserMovieInteraction, Dict[str, Any]],
    summary="Get user interaction with a specific movie",
)
async def get_movie_interaction(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
) -> Union[UserMovieInteraction, Dict[str, Any]]:
    """
    Get user's interaction with a specific movie.

    Note: Authentication is handled by the BFF layer. This endpoint trusts
    that the BFF has already verified the user_id via X-User-ID header.

    Args:
        movie_id: Movie ID
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query

    Returns:
        User's interaction with the movie, or an empty dict if no interaction exists
    """
    try:
        result = interaction_query.get_user_interaction(db, user_id, movie_id)
        return result if result else {}
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


***REMOVED*** ============================================================================
***REMOVED*** WATCHLIST COLLECTION ENDPOINTS
***REMOVED*** ============================================================================


@router.get(
    "/watchlist",
    summary="Get user's watchlist collection",
)
async def get_user_watchlist(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse:
    """
    Get user's watchlist as a collection.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        page: Page number for pagination
        limit: Maximum number of items per page

    Returns:
        Collection of movies in user's watchlist using fast-core response format

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 422 if validation fails
    """
    try:
        offset = (page - 1) * limit
        interactions, total = interaction_query.get_user_watchlist(db, user_id, limit, offset)

        ***REMOVED*** Convert to collection items
        collection_items = [
            {
                "movie_id": interaction.movie_id,
                "user_id": interaction.user_id,
                "added_at": interaction.created_at or datetime.utcnow(),
            }
            for interaction in interactions
        ]

        return responses.paginated(
            items=collection_items,
            page=page,
            limit=limit,
            total=total,
            metadata={
                "collection_type": "watchlist",
                "api_version": "v1",
                "response_pattern": "paginated",
                "service_info": {
                    "service": "backend-api",
                    "endpoint": "user_watchlist",
                },
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.post(
    "/watchlist",
    summary="Add movie to watchlist",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_watchlist(
    request: AddToCollectionRequest,
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Add a movie to user's watchlist collection.

    Args:
        request: Request containing movie_id to add
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already in watchlist
            - 422 if validation fails
    """
    try:
        interaction, was_created = interaction_service.add_to_watchlist(
            db, user_id, request.movie_id
        )

        ***REMOVED*** Make operation idempotent - return success regardless of whether it was already in watchlist
        message = (
            "Movie successfully added to watchlist"
            if was_created
            else "Movie was already in watchlist"
        )

        return responses.action(
            success=True,
            action="added_to_watchlist",
            data={
                "movie_id": request.movie_id,
                "user_id": user_id,
                "added_at": interaction.created_at or datetime.utcnow(),
                "was_already_in_watchlist": not was_created,
            },
            message=message,
            metadata={
                "collection_type": "watchlist",
                "operation": "add",
                "api_version": "v1",
                "idempotent": True,
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/watchlist/movies/{movie_id}",
    summary="Remove movie from watchlist",
)
async def remove_from_watchlist(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Remove a movie from user's watchlist collection.

    Args:
        movie_id: Movie ID to remove
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found or not in watchlist
            - 422 if validation fails
    """
    try:
        interaction, was_removed = interaction_service.remove_from_watchlist(db, user_id, movie_id)

        if not was_removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in watchlist",
            )

        return responses.action(
            success=True,
            action="removed_from_watchlist",
            data={
                "movie_id": movie_id,
                "user_id": user_id,
            },
            message="Movie successfully removed from watchlist",
            metadata={
                "collection_type": "watchlist",
                "operation": "remove",
                "api_version": "v1",
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** ============================================================================
***REMOVED*** WATCHED MOVIES COLLECTION ENDPOINTS
***REMOVED*** ============================================================================


@router.get(
    "/watched-movies",
    summary="Get user's watched movies collection",
)
async def get_user_watched_movies(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse:
    """
    Get user's watched movies as a collection.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        page: Page number for pagination
        limit: Maximum number of items per page

    Returns:
        Collection of watched movies using fast-core response format

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 422 if validation fails
    """
    try:
        offset = (page - 1) * limit
        interactions, total = interaction_query.get_user_watched_movies(db, user_id, limit, offset)

        ***REMOVED*** Convert to collection items
        collection_items = [
            {
                "movie_id": interaction.movie_id,
                "user_id": interaction.user_id,
                "added_at": interaction.created_at or datetime.utcnow(),
            }
            for interaction in interactions
        ]

        return responses.paginated(
            items=collection_items,
            page=page,
            limit=limit,
            total=total,
            metadata={
                "collection_type": "watched_movies",
                "api_version": "v1",
                "response_pattern": "paginated",
                "service_info": {
                    "service": "backend-api",
                    "endpoint": "user_watched_movies",
                },
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.post(
    "/watched-movies",
    summary="Mark movie as watched",
    status_code=status.HTTP_201_CREATED,
)
async def mark_movie_as_watched(
    request: AddToCollectionRequest,
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Mark a movie as watched by adding it to watched movies collection.

    Args:
        request: Request containing movie_id to mark as watched
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already marked as watched
            - 422 if validation fails
    """
    try:
        interaction, was_created = interaction_service.mark_as_watched(
            db, user_id, request.movie_id
        )

        ***REMOVED*** Make operation idempotent - return success regardless of whether it was already watched
        status_code = status.HTTP_201_CREATED if was_created else status.HTTP_200_OK
        message = (
            "Movie successfully marked as watched"
            if was_created
            else "Movie was already marked as watched"
        )

        return responses.action(
            success=True,
            action="marked_as_watched",
            data={
                "movie_id": request.movie_id,
                "user_id": user_id,
                "watched_at": interaction.created_at or datetime.utcnow(),
                "was_already_watched": not was_created,
            },
            message=message,
            metadata={
                "collection_type": "watched_movies",
                "operation": "add",
                "api_version": "v1",
                "idempotent": True,
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/watched-movies/{movie_id}",
    summary="Unmark movie as watched",
)
async def unmark_movie_as_watched(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Unmark a movie as watched by removing it from watched movies collection.

    Args:
        movie_id: Movie ID to unmark as watched
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found or not marked as watched
            - 422 if validation fails
    """
    try:
        interaction, was_removed = interaction_service.unmark_as_watched(db, user_id, movie_id)

        if not was_removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in watched movies",
            )

        return responses.action(
            success=True,
            action="unmarked_as_watched",
            data={
                "movie_id": movie_id,
                "user_id": user_id,
            },
            message="Movie successfully unmarked as watched",
            metadata={
                "collection_type": "watched_movies",
                "operation": "remove",
                "api_version": "v1",
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


***REMOVED*** ============================================================================
***REMOVED*** LIKED MOVIES COLLECTION ENDPOINTS
***REMOVED*** ============================================================================


@router.get(
    "/liked-movies",
    summary="Get user's liked movies collection",
)
async def get_user_liked_movies(
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_query: Annotated[UserInteractionQuery, Depends(get_user_interaction_query)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse:
    """
    Get user's liked movies as a collection.

    Args:
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_query: User interaction query
        page: Page number for pagination
        limit: Maximum number of items per page

    Returns:
        Collection of liked movies using fast-core response format

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 422 if validation fails
    """
    try:
        offset = (page - 1) * limit
        interactions, total = interaction_query.get_user_liked_movies(db, user_id, limit, offset)

        ***REMOVED*** Convert to collection items
        collection_items = [
            {
                "movie_id": interaction.movie_id,
                "user_id": interaction.user_id,
                "added_at": interaction.created_at or datetime.utcnow(),
            }
            for interaction in interactions
        ]

        return responses.paginated(
            items=collection_items,
            page=page,
            limit=limit,
            total=total,
            metadata={
                "collection_type": "liked_movies",
                "api_version": "v1",
                "response_pattern": "paginated",
                "service_info": {
                    "service": "backend-api",
                    "endpoint": "user_liked_movies",
                },
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.post(
    "/liked-movies",
    summary="Like a movie",
    status_code=status.HTTP_201_CREATED,
)
async def like_movie(
    request: AddToCollectionRequest,
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Like a movie by adding it to liked movies collection.

    Args:
        request: Request containing movie_id to like
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already liked
            - 422 if validation fails
    """
    try:
        interaction, was_created = interaction_service.like_movie(db, user_id, request.movie_id)

        ***REMOVED*** Make operation idempotent - return success regardless of whether it was already liked
        message = "Movie successfully liked" if was_created else "Movie was already liked"

        return responses.action(
            success=True,
            action="liked_movie",
            data={
                "movie_id": request.movie_id,
                "user_id": user_id,
                "liked_at": interaction.created_at or datetime.utcnow(),
                "was_already_liked": not was_created,
            },
            message=message,
            metadata={
                "collection_type": "liked_movies",
                "operation": "add",
                "api_version": "v1",
                "idempotent": True,
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)


@router.delete(
    "/liked-movies/{movie_id}",
    summary="Unlike a movie",
)
async def unlike_movie(
    movie_id: Annotated[int, Path(title="Movie ID", ge=1)],
    user_id: Annotated[int, Depends(get_user_id_from_header)],
    db: Annotated[Session, Depends(get_db)],
    interaction_service: Annotated[UserInteractionService, Depends(get_user_interaction_service)],
) -> ActionResponse:
    """
    Unlike a movie by removing it from liked movies collection.

    Args:
        movie_id: Movie ID to unlike
        user_id: User ID (authenticated by BFF) passed via X-User-ID header
        db: Database session
        interaction_service: User interaction service

    Returns:
        Operation result using fast-core action response

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found or not liked
            - 422 if validation fails
    """
    try:
        interaction, was_removed = interaction_service.unlike_movie(db, user_id, movie_id)

        if not was_removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in liked movies",
            )

        return responses.action(
            success=True,
            action="unliked_movie",
            data={
                "movie_id": movie_id,
                "user_id": user_id,
            },
            message="Movie successfully unliked",
            metadata={
                "collection_type": "liked_movies",
                "operation": "remove",
                "api_version": "v1",
            },
        )

    except ValidationError as e:
        raise service_error_to_http_exception(e)
