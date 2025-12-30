"""User interaction routes for BFF API - Resource-Oriented Design."""

from config.logging import get_logger
from fast_core.errors import ExternalServiceException
from fastapi import APIRouter, Depends, HTTPException, Path, status

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.schemas.user_interaction_schemas import (
    AddToCollectionRequest,
    CollectionOperationResponse,
    MovieCollectionItem,
    MovieCollectionResponse,
    UserMovieInteractionResponse,
)
from bff_api.services.clients import BackendClient

logger = get_logger(__name__)

router = APIRouter(tags=["user-interactions"])


# ============================================================================
# WATCHLIST COLLECTION ENDPOINTS (/me/watchlist)
# ============================================================================


@router.get(
    "/me/watchlist",
    response_model=MovieCollectionResponse,
    summary="Get user's watchlist",
)
async def get_watchlist(
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieCollectionResponse:
    """Get all movies in user's watchlist.

    Returns:
        List of movies in the user's watchlist

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    # Record user action metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_user_action("watchlist_view")

    user_id, jwt_token = user_data
    logger.debug(f"Getting watchlist for user {user_id}")

    try:
        # Backend now returns fast-core format with results, pagination, metadata
        response = await backend.get_user_watchlist(user_id, jwt_token)
        watchlist_items = response.get("results", [])

        # Convert to collection items
        items = [
            MovieCollectionItem(
                movie_id=item["movie_id"],
                user_id=item["user_id"],
                added_at=item["added_at"],  # Use added_at from new format
            )
            for item in watchlist_items
        ]

        # Use total from pagination if available, otherwise fallback to items count
        total_count = response.get("pagination", {}).get("total", len(items))
        return MovieCollectionResponse(items=items, total_count=total_count)

    except ExternalServiceException as e:
        logger.error(f"Backend error getting watchlist for user {user_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )


@router.post(
    "/me/watchlist",
    response_model=CollectionOperationResponse,
    summary="Add movie to watchlist",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_watchlist(
    request: AddToCollectionRequest,
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Add a movie to user's watchlist.

    Args:
        request: Request containing movie_id to add
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already in watchlist
            - 502 if backend service unavailable
    """
    # Record user action metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_user_action("add_to_watchlist")
    user_id, jwt_token = user_data
    movie_id = request.movie_id
    logger.debug(f"Adding movie {movie_id} to watchlist for user {user_id}")

    try:
        # Add to watchlist (backend handles idempotency)
        await backend.set_user_movie_watchlist(user_id, movie_id, jwt_token)

        # Return success regardless of whether it was already in watchlist
        return CollectionOperationResponse(
            success=True,
            message="Movie added to watchlist successfully",
            movie_id=movie_id,
            collection_type="watchlist",
        )

    except ExternalServiceException as e:
        logger.error(f"Backend error adding movie {movie_id} to watchlist for user {user_id}: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )
        elif e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


@router.delete(
    "/me/watchlist/movies/{movie_id}",
    response_model=CollectionOperationResponse,
    summary="Remove movie from watchlist",
)
async def remove_from_watchlist(
    movie_id: int = Path(..., description="Movie ID to remove", ge=1),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Remove a movie from user's watchlist.

    This operation is idempotent - removing a movie that's already not in
    the watchlist will succeed without error.

    Args:
        movie_id: Movie ID to remove from watchlist
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Removing movie {movie_id} from watchlist for user {user_id}")

    try:
        # Remove from watchlist (backend handles idempotency)
        await backend.unset_user_movie_watchlist(user_id, movie_id, jwt_token)

        return CollectionOperationResponse(
            success=True,
            message="Movie removed from watchlist successfully",
            movie_id=movie_id,
            collection_type="watchlist",
        )

    except ExternalServiceException as e:
        logger.error(
            f"Backend error removing movie {movie_id} from watchlist for user {user_id}: {e}"
        )
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


# ============================================================================
# WATCHED MOVIES COLLECTION ENDPOINTS (/me/watched-movies)
# ============================================================================


@router.get(
    "/me/watched-movies",
    response_model=MovieCollectionResponse,
    summary="Get user's watched movies",
)
async def get_watched_movies(
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieCollectionResponse:
    """Get all movies the user has watched.

    Returns:
        List of watched movies

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Getting watched movies for user {user_id}")

    try:
        # Backend now returns fast-core format with results, pagination, metadata
        response = await backend.get_user_watched_movies(user_id, jwt_token)
        watched_items = response.get("results", [])

        # Convert to collection items
        items = [
            MovieCollectionItem(
                movie_id=item["movie_id"],
                user_id=item["user_id"],
                added_at=item["added_at"],  # Use added_at from new format
            )
            for item in watched_items
        ]

        # Use total from pagination if available, otherwise fallback to items count
        total_count = response.get("pagination", {}).get("total", len(items))
        return MovieCollectionResponse(items=items, total_count=total_count)

    except ExternalServiceException as e:
        logger.error(f"Backend error getting watched movies for user {user_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )


@router.post(
    "/me/watched-movies",
    response_model=CollectionOperationResponse,
    summary="Mark movie as watched",
    status_code=status.HTTP_201_CREATED,
)
async def mark_movie_watched(
    request: AddToCollectionRequest,
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Mark a movie as watched.

    Args:
        request: Request containing movie_id to mark as watched
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already watched
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    movie_id = request.movie_id
    logger.debug(f"Marking movie {movie_id} as watched for user {user_id}")

    try:
        # Mark as watched (backend handles idempotency)
        await backend.set_user_movie_watched(user_id, movie_id, jwt_token)

        # Return success regardless of whether it was already watched
        return CollectionOperationResponse(
            success=True,
            message="Movie marked as watched successfully",
            movie_id=movie_id,
            collection_type="watched_movies",
        )

    except ExternalServiceException as e:
        logger.error(f"Backend error marking movie {movie_id} as watched for user {user_id}: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )
        elif e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


@router.delete(
    "/me/watched-movies/{movie_id}",
    response_model=CollectionOperationResponse,
    summary="Unmark movie as watched",
)
async def unmark_movie_watched(
    movie_id: int = Path(..., description="Movie ID to unmark as watched", ge=1),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Unmark a movie as watched.

    This operation is idempotent - unmarking a movie that's already not
    marked as watched will succeed without error.

    Args:
        movie_id: Movie ID to unmark as watched
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Unmarking movie {movie_id} as watched for user {user_id}")

    try:
        # Unmark as watched (backend handles idempotency)
        await backend.unset_user_movie_watched(user_id, movie_id, jwt_token)

        return CollectionOperationResponse(
            success=True,
            message="Movie unmarked as watched successfully",
            movie_id=movie_id,
            collection_type="watched_movies",
        )

    except ExternalServiceException as e:
        logger.error(f"Backend error unmarking movie {movie_id} as watched for user {user_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


# ============================================================================
# LIKED MOVIES COLLECTION ENDPOINTS (/me/liked-movies)
# ============================================================================


@router.get(
    "/me/liked-movies",
    response_model=MovieCollectionResponse,
    summary="Get user's liked movies",
)
async def get_liked_movies(
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieCollectionResponse:
    """Get all movies the user has liked.

    Returns:
        List of liked movies

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Getting liked movies for user {user_id}")

    try:
        # Backend now returns fast-core format with results, pagination, metadata
        response = await backend.get_user_liked_movies(user_id, jwt_token)
        liked_items = response.get("results", [])

        # Convert to collection items
        items = [
            MovieCollectionItem(
                movie_id=item["movie_id"],
                user_id=item["user_id"],
                added_at=item["added_at"],  # Use added_at from new format
            )
            for item in liked_items
        ]

        # Use total from pagination if available, otherwise fallback to items count
        total_count = response.get("pagination", {}).get("total", len(items))
        return MovieCollectionResponse(items=items, total_count=total_count)

    except ExternalServiceException as e:
        logger.error(f"Backend error getting liked movies for user {user_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )


@router.post(
    "/me/liked-movies",
    response_model=CollectionOperationResponse,
    summary="Like a movie",
    status_code=status.HTTP_201_CREATED,
)
async def like_movie(
    request: AddToCollectionRequest,
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Like a movie.

    Args:
        request: Request containing movie_id to like
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 409 if movie already liked
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    movie_id = request.movie_id
    logger.debug(f"Liking movie {movie_id} for user {user_id}")

    try:
        # Like the movie (backend handles idempotency)
        await backend.set_user_movie_liked(user_id, movie_id, jwt_token)

        # Return success regardless of whether it was already liked
        return CollectionOperationResponse(
            success=True,
            message="Movie liked successfully",
            movie_id=movie_id,
            collection_type="liked_movies",
        )

    except ExternalServiceException as e:
        logger.error(f"Backend error liking movie {movie_id} for user {user_id}: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )
        elif e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


@router.delete(
    "/me/liked-movies/{movie_id}",
    response_model=CollectionOperationResponse,
    summary="Unlike a movie",
)
async def unlike_movie(
    movie_id: int = Path(..., description="Movie ID to unlike", ge=1),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> CollectionOperationResponse:
    """Unlike a movie.

    This operation is idempotent - unliking a movie that's already not
    liked will succeed without error.

    Args:
        movie_id: Movie ID to unlike
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Operation result

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Unliking movie {movie_id} for user {user_id}")

    try:
        # Unlike the movie (backend handles idempotency)
        await backend.unset_user_movie_liked(user_id, movie_id, jwt_token)

        return CollectionOperationResponse(
            success=True,
            message="Movie unliked successfully",
            movie_id=movie_id,
            collection_type="liked_movies",
        )

    except ExternalServiceException as e:
        logger.error(f"Backend error unliking movie {movie_id} for user {user_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except HTTPException:
        raise


# ============================================================================
# INDIVIDUAL MOVIE INTERACTION ENDPOINT (for compatibility)
# ============================================================================


@router.get(
    "/me/interactions/movies/{movie_id}",
    response_model=UserMovieInteractionResponse,
    summary="Get user interaction with a movie",
)
async def get_movie_interaction(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Get user's interaction status for a specific movie.

    Args:
        movie_id: Movie ID to get interaction for
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        User's interaction status for the movie

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if no interaction found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.debug(f"Getting interaction for user {user_id}, movie {movie_id}")

    try:
        interaction = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        if not interaction:
            # Return default interaction (all false)
            from datetime import datetime

            now = datetime.utcnow().isoformat() + "Z"
            return UserMovieInteractionResponse(
                user_id=user_id,
                movie_id=movie_id,
                watched=False,
                liked=False,
                in_watchlist=False,
                created_at=now,
                updated_at=now,
            )

        return UserMovieInteractionResponse(**interaction)

    except ExternalServiceException as e:
        logger.error(f"Backend error getting interaction for user {user_id}, movie {movie_id}: {e}")
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
