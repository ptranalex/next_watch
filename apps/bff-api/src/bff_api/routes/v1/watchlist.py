"""Watchlist movies-related routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query, status

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies import get_backend_client
from bff_api.services.clients import BackendClient
from fast_core.responses import ResponseBuilder
from fast_core.errors import ExternalServiceException
from bff_api.core.metrics import get_bff_metrics

logger = get_logger(__name__)

router = APIRouter(tags=["watchlist"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)


async def _get_user_watchlist(
    backend: BackendClient,
    user_id: int,
    jwt_token: str,
    limit: int,
    page: int,
) -> Dict[str, Any]:
    """Get user's watchlist interactions from backend.

    Args:
        backend: Backend client
        user_id: User ID
        jwt_token: JWT token for authentication
        limit: Number of items to fetch
        page: Page number for pagination

    Returns:
        Watchlist interactions response

    Raises:
        ExternalServiceException: If backend request fails
    """
    return await backend.get_user_watchlist(
        user_id=user_id,
        jwt_token=jwt_token,
        limit=limit,
        page=page,
    )


async def _get_movies_bulk(
    backend: BackendClient,
    movie_ids: List[int],
    user_id: int,
    page: int = 1,
    limit: int = 100,
) -> Dict[str, Any]:
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


@router.get("/watchlist")
async def get_user_watchlist(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    ***REMOVED*** Filter parameters
    imdb_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum IMDb rating"),
    rotten_tomatoes_rating: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum Metacritic rating"
    ),
    year: Optional[int] = Query(None, ge=1900, le=2030, description="Release year"),
    sort_by: str = Query(
        "title",
        description="Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get user's watchlist movies with full movie details.

    Provides a paginated list of movies that the authenticated user has added
    to their watchlist, including their interaction data and movie details.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        imdb_rating: Filter by minimum IMDb rating
        rotten_tomatoes_rating: Filter by minimum Rotten Tomatoes rating
        metacritic_rating: Filter by minimum Metacritic rating
        year: Filter by release year
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order
        user_data: Authenticated user ID and JWT token
        backend: Backend HTTP client dependency

    Returns:
        Paginated list of watchlist movies with full details and user interactions

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service is unavailable
    """
    ***REMOVED*** Record user action metrics
    metrics = get_bff_metrics()
    if metrics:
        metrics.record_user_action("watchlist_view")

    user_id, jwt_token = user_data

    logger.debug(f"📋 Fetching watchlist for user {user_id} (page {page}, limit {limit})")

    try:
        ***REMOVED*** Get watchlist interactions from backend using new collection API
        watchlist_interactions_response = await _get_user_watchlist(
            backend=backend,
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            page=page,
        )

        ***REMOVED*** The new backend returns fast-core ResponseBuilder format with results array
        ***REMOVED*** Extract the collection items from the response
        collection_items: List[Dict[str, Any]] = watchlist_interactions_response.get("results", [])

        ***REMOVED*** Convert collection items to interaction format for compatibility
        ***REMOVED*** Collection items have: {movie_id, user_id, added_at}
        ***REMOVED*** We need to convert them to interaction format: {movie_id, in_watchlist: True, ...}
        actually_watchlisted = [
            {
                "movie_id": item.get("movie_id"),
                "user_id": item.get("user_id"),
                "in_watchlist": True,  ***REMOVED*** Always true for watchlist collection items
                "watched": False,  ***REMOVED*** We don't have this info from collection endpoint
                "liked": False,  ***REMOVED*** We don't have this info from collection endpoint
                "created_at": item.get("added_at"),
            }
            for item in collection_items
            if item.get("movie_id") is not None
        ]

        if not actually_watchlisted:
            logger.debug(f"No watchlist movies found for user {user_id}")
            response = responses.paginated(
                items=[],
                page=page,
                limit=limit,
                total=0,
                metadata={
                    "filters_applied": {
                        "imdb_rating": imdb_rating,
                        "rotten_tomatoes_rating": rotten_tomatoes_rating,
                        "metacritic_rating": metacritic_rating,
                        "year": year,
                        "sort_by": sort_by,
                        "sort_desc": sort_desc,
                    },
                    "service_info": {
                        "aggregated_from": ["backend-api"],
                        "user_authenticated": True,
                        "user_personalized": True,
                    },
                    "api_version": "v1",
                    "response_pattern": "paginated",
                    "collection_type": "watchlist_movies",
                    "user_context": {"user_id": user_id},
                },
            )
            return cast(Dict[str, Any], response)

        ***REMOVED*** Extract movie IDs for bulk fetching - filter out None values first and then convert to int
        valid_movie_ids = [
            mid
            for mid in [interaction.get("movie_id") for interaction in actually_watchlisted]
            if mid is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.debug(f"No valid movie IDs found in watchlist interactions for user {user_id}")
            response = responses.paginated(
                items=[],
                page=page,
                limit=limit,
                total=0,
                metadata={
                    "filters_applied": {
                        "imdb_rating": imdb_rating,
                        "rotten_tomatoes_rating": rotten_tomatoes_rating,
                        "metacritic_rating": metacritic_rating,
                        "year": year,
                        "sort_by": sort_by,
                        "sort_desc": sort_desc,
                    },
                    "service_info": {
                        "aggregated_from": ["backend-api"],
                        "user_authenticated": True,
                        "user_personalized": True,
                    },
                    "api_version": "v1",
                    "response_pattern": "paginated",
                    "collection_type": "watchlist_movies",
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
            for interaction in actually_watchlisted
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
                enriched_movie["watched"] = interaction.get("watched", False)
                enriched_movie["liked"] = interaction.get("liked", False)
                enriched_movie["in_watchlist"] = interaction.get(
                    "in_watchlist", True
                )  ***REMOVED*** Always true for watchlist movies

                ***REMOVED*** Ensure user_interactions object is present with complete structure
                enriched_movie["user_interactions"] = {
                    "in_watchlist": interaction.get(
                        "in_watchlist", True
                    ),  ***REMOVED*** Always true for watchlist movies
                    "is_favorite": interaction.get("liked", False),
                    "user_rating": interaction.get("user_rating"),
                    "watch_progress": interaction.get("watch_progress", 0),
                    "is_watched": interaction.get("watched", False),
                }

                enriched_movies.append(enriched_movie)

        ***REMOVED*** Apply filtering to the enriched movies (since we now have full movie data)
        if enriched_movies:
            if imdb_rating is not None:
                enriched_movies = [
                    m
                    for m in enriched_movies
                    if m.get("imdb_rating") and cast(float, m.get("imdb_rating")) >= imdb_rating
                ]
            if rotten_tomatoes_rating is not None:
                enriched_movies = [
                    m
                    for m in enriched_movies
                    if m.get("rotten_tomatoes_rating")
                    and cast(float, m.get("rotten_tomatoes_rating")) >= rotten_tomatoes_rating
                ]
            if metacritic_rating is not None:
                enriched_movies = [
                    m
                    for m in enriched_movies
                    if m.get("metacritic_rating")
                    and cast(float, m.get("metacritic_rating")) >= metacritic_rating
                ]
            if year is not None:
                enriched_movies = [
                    m
                    for m in enriched_movies
                    if m.get("release_date")
                    and str(m.get("release_date", "")).startswith(str(year))
                ]

            ***REMOVED*** Apply sorting
            reverse = sort_desc
            if sort_by == "title":
                enriched_movies.sort(key=lambda x: (x.get("title") or "").lower(), reverse=reverse)
            elif sort_by == "release_date":
                enriched_movies.sort(
                    key=lambda x: x.get("release_date") or "1900-01-01", reverse=reverse
                )
            elif sort_by == "imdb_rating":
                enriched_movies.sort(key=lambda x: x.get("imdb_rating") or 0, reverse=reverse)
            elif sort_by == "rotten_tomatoes_rating":
                enriched_movies.sort(
                    key=lambda x: x.get("rotten_tomatoes_rating") or 0, reverse=reverse
                )
            elif sort_by == "metacritic_rating":
                enriched_movies.sort(key=lambda x: x.get("metacritic_rating") or 0, reverse=reverse)

        ***REMOVED*** Calculate pagination metadata using backend response pagination data
        backend_pagination = watchlist_interactions_response.get("pagination", {})
        total_count = backend_pagination.get("total", len(enriched_movies))
        has_next = backend_pagination.get("has_next", len(actually_watchlisted) == limit)
        has_prev = backend_pagination.get("has_prev", page > 1)
        total_pages = backend_pagination.get("total_pages", 1)

        ***REMOVED*** Use ResponseBuilder paginated pattern for consistent response structure
        response = responses.paginated(
            items=enriched_movies,
            page=page,
            limit=limit,
            total=total_count,
            metadata={
                "filters_applied": {
                    "imdb_rating": imdb_rating,
                    "rotten_tomatoes_rating": rotten_tomatoes_rating,
                    "metacritic_rating": metacritic_rating,
                    "year": year,
                    "sort_by": sort_by,
                    "sort_desc": sort_desc,
                },
                "service_info": {
                    "aggregated_from": ["backend-api"],
                    "user_authenticated": True,
                    "user_personalized": True,
                },
                "api_version": "v1",
                "response_pattern": "paginated",
                "collection_type": "watchlist_movies",
                "user_context": {"user_id": user_id},
                "collection_stats": {
                    "total_watchlisted": total_count,
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
        return cast(Dict[str, Any], response)

    except ExternalServiceException as e:
        logger.error(
            "Backend service error for watchlist movies",
            error=str(e),
            service="bff",
            endpoint="watchlist_movies",
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
            "Internal error processing watchlist movies request",
            error=str(e),
            service="bff",
            endpoint="watchlist_movies",
            user_id=user_id,
            exc_info=True,  ***REMOVED*** Include stack trace for debugging
        )
        ***REMOVED*** Return 500 for internal errors (bugs in our code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )
