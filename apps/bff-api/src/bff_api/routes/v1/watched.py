"""Watched movies-related routes for BFF API."""

from typing import Any, cast

from config.logging import get_logger
from fast_core.errors import ExternalServiceException
from fast_core.responses import ResponseBuilder
from fastapi import APIRouter, Depends, HTTPException, Query, status

from bff_api.core.metrics import get_bff_metrics
from bff_api.dependencies import get_backend_client
from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.services.clients import BackendClient

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


async def _get_user_watched_movies(
    backend: BackendClient,
    user_id: int,
    jwt_token: str,
    limit: int,
    page: int,
) -> dict[str, Any]:
    """Get user's watched movie interactions from backend.

    Args:
        backend: Backend client
        user_id: User ID
        jwt_token: JWT token for authentication
        limit: Number of items to fetch
        page: Page number for pagination

    Returns:
        Watched movies interactions response

    Raises:
        ExternalServiceException: If backend request fails
    """
    return await backend.get_user_watched_movies(
        user_id=user_id,
        jwt_token=jwt_token,
        limit=limit,
        page=page,
    )


async def _get_movies_bulk(
    backend: BackendClient,
    movie_ids: list[int],
    user_id: int,
    page: int = 1,
    limit: int = 100,
) -> dict[str, Any]:
    """Get movie details in bulk from backend.

    Args:
        backend: Backend client
        movie_ids: List of movie IDs to fetch
        user_id: User ID for personalized content
        page: Page number
        limit: Number of items per page

    Returns:
        Movies bulk response

    Raises:
        ExternalServiceException: If backend request fails
    """
    return await backend.get_movies_bulk(
        movie_ids=movie_ids,
        user_id=user_id,
        page=page,
        limit=limit,
    )


@router.get("/watched")
async def get_watched_movies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> dict[str, Any]:
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
            - 500 if internal server error occurs
            - 502 if backend service is unavailable
    """
    ***REMOVED*** Record user action metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_user_action("watched_view")

    user_id, jwt_token = user_data

    logger.debug(f"🎬 Fetching watched movies for user {user_id} (page {page}, limit {limit})")

    try:
        ***REMOVED*** Get watched movies interactions from backend
        watched_interactions_response = await _get_user_watched_movies(
            backend=backend,
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            page=page,
        )

        ***REMOVED*** The backend client now returns fast-core format with {"results": [...]} format
        ***REMOVED*** Extract the collection items from the watched-movies collection endpoint
        watched_collection_items: list[dict[str, Any]] = watched_interactions_response.get(
            "results", []
        )

        ***REMOVED*** All items from the watched-movies collection are watched by definition
        ***REMOVED*** No need to filter - these are already the watched movies
        actually_watched = watched_collection_items

        if not actually_watched:
            logger.debug(f"No watched movies found for user {user_id}")
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
            return cast(dict[str, Any], response)

        ***REMOVED*** Extract movie IDs for bulk fetching - collection items have movie_id directly
        valid_movie_ids = [
            item["movie_id"] for item in actually_watched if item.get("movie_id") is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.debug(f"No valid movie IDs found in watched interactions for user {user_id}")
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
            return cast(dict[str, Any], response)

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

        ***REMOVED*** Create a mapping of movie_id to collection item data for efficient lookup
        collection_item_map = {
            item["movie_id"]: item for item in actually_watched if item.get("movie_id")
        }

        ***REMOVED*** Merge movie details with collection item data
        enriched_movies: list[dict[str, Any]] = []
        for movie in movies_data:
            movie_id = movie.get("id")
            if movie_id and movie_id in collection_item_map:
                collection_item = collection_item_map[movie_id]

                ***REMOVED*** Merge collection item data with movie details
                enriched_movie = {**movie}

                ***REMOVED*** Set the frontend-expected interaction fields for watched movies
                enriched_movie["watched"] = (
                    True  ***REMOVED*** Always true since this is from watched collection
                )
                enriched_movie["liked"] = (
                    False  ***REMOVED*** Unknown from collection data, would need separate lookup
                )
                enriched_movie["in_watchlist"] = (
                    False  ***REMOVED*** Unknown from collection data, would need separate lookup
                )

                ***REMOVED*** Ensure user_interactions object is present with complete structure
                enriched_movie["user_interactions"] = {
                    "in_watchlist": False,  ***REMOVED*** Unknown from collection data
                    "is_favorite": False,  ***REMOVED*** Unknown from collection data
                    "user_rating": None,  ***REMOVED*** Unknown from collection data
                    "watch_progress": 100,  ***REMOVED*** Assume 100% for watched movies
                    "is_watched": True,  ***REMOVED*** Always true for watched movies
                    "watched_at": collection_item.get("added_at"),  ***REMOVED*** Use added_at as watched_at
                }

                enriched_movies.append(enriched_movie)

        ***REMOVED*** Calculate pagination metadata using backend response pagination data
        backend_pagination = watched_interactions_response.get("pagination", {})
        total_count = backend_pagination.get("total", len(enriched_movies))
        has_next = backend_pagination.get("has_next", len(actually_watched) == limit)
        has_prev = backend_pagination.get("has_prev", page > 1)
        total_pages = backend_pagination.get("total_pages", 1)

        logger.debug(
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
                    "total_watched": total_count,
                    "current_page_count": len(enriched_movies),
                    "backend_total": backend_pagination.get("total", "unknown"),
                },
                "pagination_source": "backend",
                "backend_pagination": backend_pagination,
            },
        )

        ***REMOVED*** Manually update pagination fields if ResponseBuilder doesn't support them directly
        if isinstance(response, dict) and "pagination" in response:
            response["pagination"].update(
                {
                    "has_next": has_next,
                    "has_prev": has_prev,
                    "total_pages": total_pages,
                }
            )
        return cast(dict[str, Any], response)

    except ExternalServiceException as e:
        logger.error(
            "Backend service error for watched movies",
            error=str(e),
            service="bff",
            endpoint="watched_movies",
            user_id=user_id,
            status_code=e.status_code,
        )
        ***REMOVED*** Map backend service errors to appropriate HTTP status codes
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )
        else:
            ***REMOVED*** This is a legitimate backend service issue (down, timeout, etc.)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Backend service unavailable",
            )
    except Exception as e:
        logger.error(
            "Internal error processing watched movies request",
            error=str(e),
            service="bff",
            endpoint="watched_movies",
            user_id=user_id,
            exc_info=True,  ***REMOVED*** Include stack trace for debugging
        )
        ***REMOVED*** Return 500 for internal errors (bugs in our code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )
