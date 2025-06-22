"""User interaction routes for BFF API."""

from typing import Tuple

from config.logging import get_logger
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from fast_core.errors import ExternalServiceException

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies import get_backend_client
from bff_api.schemas.user_interaction_schemas import (
    ToggleInteractionRequest,
    ToggleInteractionResponse,
    UserMovieInteractionResponse,
)
from bff_api.services.clients import BackendClient

logger = get_logger(__name__)

router = APIRouter(tags=["user-interactions"])


***REMOVED*** ============================================================================
***REMOVED*** New RESTful endpoints for user interactions
***REMOVED*** ============================================================================


@router.put(
    "/user/interactions/movies/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Mark a movie as watched",
)
async def set_movie_watched(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Mark a movie as watched.

    Sets the watched status to true for a specific movie.

    Args:
        movie_id: Movie ID to mark as watched
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting watched=true for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if not already watched
        if current is None or not current.get("watched", False):
            result = await backend.set_user_movie_watched(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state
        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error setting watched for user {user_id}, movie {movie_id}: {e}")
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


@router.delete(
    "/user/interactions/movies/{movie_id}/watched",
    response_model=UserMovieInteractionResponse,
    summary="Unmark a movie as watched",
)
async def unset_movie_watched(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Unmark a movie as watched.

    Sets the watched status to false for a specific movie.

    Args:
        movie_id: Movie ID to unmark as watched
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting watched=false for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if currently watched
        if current is not None and current.get("watched", False):
            result = await backend.unset_user_movie_watched(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state or no interaction exists
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )

        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error unsetting watched for user {user_id}, movie {movie_id}: {e}")
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


@router.put(
    "/user/interactions/movies/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Like a movie",
)
async def set_movie_liked(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Like a movie.

    Sets the liked status to true for a specific movie.

    Args:
        movie_id: Movie ID to like
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting liked=true for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if not already liked
        if current is None or not current.get("liked", False):
            result = await backend.set_user_movie_liked(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state
        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error setting liked for user {user_id}, movie {movie_id}: {e}")
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


@router.delete(
    "/user/interactions/movies/{movie_id}/liked",
    response_model=UserMovieInteractionResponse,
    summary="Unlike a movie",
)
async def unset_movie_liked(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Unlike a movie.

    Sets the liked status to false for a specific movie.

    Args:
        movie_id: Movie ID to unlike
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting liked=false for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if currently liked
        if current is not None and current.get("liked", False):
            result = await backend.unset_user_movie_liked(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state or no interaction exists
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )

        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error unsetting liked for user {user_id}, movie {movie_id}: {e}")
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


@router.put(
    "/user/interactions/movies/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Add movie to watchlist",
)
async def set_movie_watchlist(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Add a movie to watchlist.

    Sets the in_watchlist status to true for a specific movie.

    Args:
        movie_id: Movie ID to add to watchlist
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting in_watchlist=true for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if not already in watchlist
        if current is None or not current.get("in_watchlist", False):
            result = await backend.set_user_movie_watchlist(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state
        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error setting watchlist for user {user_id}, movie {movie_id}: {e}")
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


@router.delete(
    "/user/interactions/movies/{movie_id}/watchlist",
    response_model=UserMovieInteractionResponse,
    summary="Remove movie from watchlist",
)
async def unset_movie_watchlist(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Remove a movie from watchlist.

    Sets the in_watchlist status to false for a specific movie.

    Args:
        movie_id: Movie ID to remove from watchlist
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Updated user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    logger.info(f"Setting in_watchlist=false for user {user_id}, movie {movie_id}")

    try:
        ***REMOVED*** Get current interaction
        current = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        ***REMOVED*** Only toggle if currently in watchlist
        if current is not None and current.get("in_watchlist", False):
            result = await backend.unset_user_movie_watchlist(user_id, movie_id, jwt_token)
            return UserMovieInteractionResponse(**result)

        ***REMOVED*** Already in desired state or no interaction exists
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )

        return UserMovieInteractionResponse(**current)

    except ExternalServiceException as e:
        logger.error(f"Backend error unsetting watchlist for user {user_id}, movie {movie_id}: {e}")
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


***REMOVED*** ============================================================================
***REMOVED*** Legacy toggle endpoint (maintained for backwards compatibility)
***REMOVED*** ============================================================================


@router.post(
    "/user/interactions/{movie_id}/toggle",
    response_model=ToggleInteractionResponse,
    summary="Toggle user interaction with a movie (legacy)",
    deprecated=True,
)
async def toggle_user_interaction(
    request: ToggleInteractionRequest,
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> ToggleInteractionResponse:
    """Toggle a specific user interaction with a movie.

    Allows toggling of user movie interactions including:
    - watched: Mark/unmark movie as watched
    - liked: Like/unlike a movie
    - in_watchlist: Add/remove movie from watchlist

    NOTE: This endpoint is deprecated. Please use the specific PUT/DELETE
    endpoints for each interaction type.

    Args:
        movie_id: Movie ID to interact with
        request: Toggle interaction request data
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        Toggle interaction response with updated interaction data

    Raises:
        HTTPException:
            - 400 if invalid interaction type
            - 401 if not authenticated
            - 404 if movie not found
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data
    interaction_type = request.interaction_type

    logger.info(f"User {user_id} toggling {interaction_type} for movie {movie_id}")

    try:
        ***REMOVED*** Call appropriate backend toggle method based on interaction type
        if interaction_type == "watched":
            result = await backend.toggle_user_movie_watched(user_id, movie_id, jwt_token)
        elif interaction_type == "liked":
            result = await backend.toggle_user_movie_liked(user_id, movie_id, jwt_token)
        elif interaction_type == "in_watchlist":
            result = await backend.toggle_user_movie_watchlist(user_id, movie_id, jwt_token)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interaction type: {interaction_type}",
            )

        ***REMOVED*** Convert backend response to our schema
        interaction = UserMovieInteractionResponse(**result)

        ***REMOVED*** Determine the action that was performed based on the result
        action_map = {
            "watched": "watched" if interaction.watched else "unwatched",
            "liked": "liked" if interaction.liked else "unliked",
            "in_watchlist": (
                "added to watchlist" if interaction.in_watchlist else "removed from watchlist"
            ),
        }

        action = action_map[interaction_type]
        message = f"Movie {action} successfully"

        logger.info(
            f"Successfully toggled {interaction_type} for user {user_id}, movie {movie_id}: {action}"
        )

        return ToggleInteractionResponse(
            success=True,
            message=message,
            interaction=interaction,
        )

    except ExternalServiceException as e:
        logger.error(
            f"Backend error toggling {interaction_type} for user {user_id}, movie {movie_id}: {e}"
        )
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


@router.get(
    "/user/interactions/{movie_id}",
    response_model=UserMovieInteractionResponse,
    summary="Get user interaction with a movie",
)
async def get_user_interaction(
    movie_id: int = Path(..., description="Movie ID", ge=1),
    user_data: Tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> UserMovieInteractionResponse:
    """Get user's current interaction with a specific movie.

    Args:
        movie_id: Movie ID to get interaction for
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

    Returns:
        User movie interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 404 if movie not found or no interaction exists
            - 502 if backend service unavailable
    """
    user_id, jwt_token = user_data

    logger.info(f"Getting interaction for user {user_id}, movie {movie_id}")

    try:
        result = await backend.get_user_movie_interaction(user_id, movie_id, jwt_token)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No interaction found for this movie",
            )

        return UserMovieInteractionResponse(**result)

    except ExternalServiceException as e:
        logger.error(f"Backend error getting interaction for user {user_id}, movie {movie_id}: {e}")
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
