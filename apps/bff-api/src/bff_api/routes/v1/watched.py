"""Watched movies-related routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies import get_backend_client
from fast_core.responses import ResponseBuilder

logger = get_logger(__name__)
router = APIRouter(tags=["watched"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)


def _build_api_path(path: str) -> str:
    """Build API path with version prefix.

    Args:
        path: Relative API path

    Returns:
        Full API path with version prefix
    """
    ***REMOVED*** Remove leading slash if present to avoid double slashes
    clean_path = path.lstrip("/")
    return f"/api/v1/{clean_path}"


async def _handle_backend_error(e: Exception, operation: str, **context: Any) -> None:
    """Handle backend service errors consistently.

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        **context: Additional context for logging
    """
    logger.error(
        f"Backend error for {operation}", error=str(e), service="bff", endpoint=operation, **context
    )
    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 401:
        raise HTTPException(status_code=401, detail="Authentication failed")
    else:
        raise HTTPException(status_code=502, detail="Backend service unavailable")


async def _get_user_watched_movies(
    backend: httpx.AsyncClient,
    user_id: int,
    jwt_token: str,
    limit: int,
    offset: int,
) -> Dict[str, Any]:
    """Get user's watched movie interactions from backend.

    Args:
        backend: HTTP client for backend service
        user_id: User ID
        jwt_token: JWT token for authentication
        limit: Number of items to fetch
        offset: Offset for pagination

    Returns:
        Watched movies interactions response

    Raises:
        httpx.HTTPStatusError: If HTTP request fails
        httpx.RequestError: If request cannot be made
    """
    response = await backend.get(
        _build_api_path(f"/users/{user_id}/interactions/watched"),
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    response.raise_for_status()
    return cast(Dict[str, Any], response.json())


async def _get_movies_bulk(
    backend: httpx.AsyncClient,
    movie_ids: List[int],
    user_id: int,
    page: int = 1,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get movie details in bulk from backend.

    Args:
        backend: HTTP client for backend service
        movie_ids: List of movie IDs to fetch
        user_id: User ID for personalized content
        page: Page number
        limit: Number of items per page

    Returns:
        Movies bulk response

    Raises:
        httpx.HTTPStatusError: If HTTP request fails
        httpx.RequestError: If request cannot be made
    """
    params: Dict[str, Union[str, int, List[int]]] = {
        "movie_ids": movie_ids,
        "user_id": user_id,
        "page": page,
        "limit": limit,
    }

    response = await backend.post(
        _build_api_path("/movies/bulk"),
        json={"movie_ids": movie_ids},
        params={"user_id": user_id, "page": page, "limit": limit},
    )
    response.raise_for_status()
    return cast(Dict[str, Any], response.json())


@router.get("/watched")
async def get_watched_movies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: httpx.AsyncClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get user's watched movies.

    Provides a paginated list of movies that the authenticated user has marked
    as watched, including their interaction data and movie details.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        user_data: Authenticated user ID and JWT token
        backend: Backend HTTP client dependency

    Returns:
        Paginated list of watched movies with user interaction data

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service is unavailable
    """
    user_id, jwt_token = user_data

    ***REMOVED*** Calculate offset for pagination
    offset = (page - 1) * limit

    logger.info(f"🎬 Fetching watched movies for user {user_id} (page {page}, limit {limit})")

    try:
        ***REMOVED*** Get watched movies interactions from backend
        watched_interactions_response = await _get_user_watched_movies(
            backend=backend,
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            offset=offset,
        )

        ***REMOVED*** The backend client wraps list responses in {"data": [...]} format
        ***REMOVED*** Extract the interactions list from the wrapped response
        watched_interactions: List[Dict[str, Any]] = watched_interactions_response.get("data", [])

        ***REMOVED*** Filter to only get actually watched movies (since some interactions might have watched=false)
        actually_watched = [
            interaction for interaction in watched_interactions if interaction.get("watched", False)
        ]

        if not actually_watched:
            logger.info(f"No watched movies found for user {user_id}")
            response = responses.paginated(
                items=[],
                page=page,
                limit=limit,
                total=0,
                metadata={
                    "service_info": {
                        "aggregated_from": ["backend-api"],
                        "user_authenticated": True,
                        "user_personalized": True,
                    },
                    "api_version": "v1",
                    "response_pattern": "paginated",
                    "collection_type": "watched_movies",
                    "user_context": {"user_id": user_id},
                },
            )
            return cast(Dict[str, Any], response)

        ***REMOVED*** Extract movie IDs for bulk fetching - filter out None values first and then convert to int
        valid_movie_ids = [
            mid
            for mid in [interaction.get("movie_id") for interaction in actually_watched]
            if mid is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.info(f"No valid movie IDs found in watched interactions for user {user_id}")
            response = responses.paginated(
                items=[],
                page=page,
                limit=limit,
                total=0,
                metadata={
                    "service_info": {
                        "aggregated_from": ["backend-api"],
                        "user_authenticated": True,
                        "user_personalized": True,
                    },
                    "api_version": "v1",
                    "response_pattern": "paginated",
                    "collection_type": "watched_movies",
                    "user_context": {"user_id": user_id},
                    "error": "No valid movie IDs found",
                },
            )
            return cast(Dict[str, Any], response)

        ***REMOVED*** Fetch movie details in bulk
        try:
            movies_response = await _get_movies_bulk(
                backend=backend,
                movie_ids=movie_ids,
                user_id=user_id,
                page=1,  ***REMOVED*** Get all movies in one request since we already paginated the interactions
                limit=len(movie_ids),  ***REMOVED*** Get all movies
            )

            movies_data = movies_response.get("results", [])

        except Exception as e:
            logger.error(f"Failed to fetch bulk movie details for user {user_id}: {e}")
            ***REMOVED*** Fallback to empty response instead of failing completely
            movies_data = []

        ***REMOVED*** Create a mapping of movie_id to interaction data for efficient lookup
        interaction_map = {
            interaction.get("movie_id"): interaction
            for interaction in actually_watched
            if interaction.get("movie_id")
        }

        ***REMOVED*** Merge movie details with interaction data
        enriched_movies: List[Dict[str, Any]] = []
        for movie in movies_data:
            movie_id = movie.get("id")
            if movie_id and movie_id in interaction_map:
                interaction = interaction_map[movie_id]

                ***REMOVED*** Merge interaction data with movie details
                enriched_movie = {**movie}

                ***REMOVED*** Set the frontend-expected interaction fields
                enriched_movie["watched"] = interaction.get("watched", True)
                enriched_movie["liked"] = interaction.get("liked", False)
                enriched_movie["in_watchlist"] = interaction.get("in_watchlist", False)

                ***REMOVED*** Ensure user_interactions object is present with complete structure
                enriched_movie["user_interactions"] = {
                    "in_watchlist": interaction.get("in_watchlist", False),
                    "is_favorite": interaction.get("liked", False),
                    "user_rating": interaction.get("user_rating"),
                    "watch_progress": interaction.get(
                        "watch_progress", 100
                    ),  ***REMOVED*** Assume 100% for watched movies
                    "is_watched": True,  ***REMOVED*** Always true for watched movies
                }

                enriched_movies.append(enriched_movie)

        ***REMOVED*** Calculate pagination metadata based on the original interactions
        total_count = len(enriched_movies)
        has_next = (
            len(actually_watched) == limit
        )  ***REMOVED*** If we got a full page of interactions, assume there might be more
        has_prev = page > 1
        total_pages = page if not has_next else page + 1  ***REMOVED*** Estimate based on current page

        logger.info(
            f"✅ Returning {len(enriched_movies)} watched movies for user {user_id} (enriched from {len(actually_watched)} interactions)"
        )

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=enriched_movies,
            page=page,
            limit=limit,
            total=total_count,
            metadata={
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": True,
                    "user_personalized": True,
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "collection_type": "watched_movies",
                "user_context": {"user_id": user_id},
                "collection_stats": {
                    "total_watched": len(actually_watched),
                    "returned_count": len(enriched_movies),
                },
            },
        )
        return cast(Dict[str, Any], response)

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        await _handle_backend_error(e, "watched_movies", user_id=user_id)
        ***REMOVED*** This line is unreachable but satisfies type checker
        response = responses.paginated(
            items=[],
            page=page,
            limit=limit,
            total=0,
            metadata={
                "error": "Backend service unavailable",
                "service_info": {"aggregated_from": ["backend-api"]},
                "api_version": "v1",
                "response_pattern": "paginated",
                "collection_type": "watched_movies",
                "user_context": {"user_id": user_id},
            },
        )
        return cast(Dict[str, Any], response)
