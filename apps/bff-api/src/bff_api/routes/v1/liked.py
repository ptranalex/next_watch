"""Liked movies-related routes for BFF API."""

from typing import Any, Dict, List, Optional, cast

from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fast_core.errors import service_error_handler, ExternalServiceException
from fast_core.responses import ResponseBuilder

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies import get_backend_client
from bff_api.services.clients import BackendClient

logger = get_logger(__name__)
router = APIRouter(tags=["liked"])

***REMOVED*** Initialize response builder for consistent API responses
responses = ResponseBuilder(
    config={
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
        },
    }
)


@service_error_handler("backend-api", logger, "get_user_liked_movies")
async def _get_user_liked_movies(
    backend: BackendClient,
    user_id: int,
    jwt_token: str,
    limit: int,
    page: int,
) -> Dict[str, Any]:
    """Get user's liked movie interactions from backend.

    Args:
        backend: Backend client
        user_id: User ID
        jwt_token: JWT token for authentication
        limit: Number of items to fetch
        page: Page number for pagination

    Returns:
        Liked movies interactions response

    Raises:
        ExternalServiceException: If request fails
    """
    return await backend.get_user_liked_movies(
        user_id=user_id,
        jwt_token=jwt_token,
        limit=limit,
        page=page,
    )


@service_error_handler("backend-api", logger, "get_movies_bulk")
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
        ExternalServiceException: If request fails
    """
    return await backend.get_movies_bulk(
        movie_ids=movie_ids,
        user_id=user_id,
        page=page,
        limit=limit,
    )


@router.get("/liked")
async def get_user_liked_movies(
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
    """Get user's liked movies with full movie details.

    Provides a paginated list of movies that the authenticated user has liked,
    including their interaction data and movie details.

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
        Paginated list of liked movies with full details and user interactions

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 500 if internal server error occurs
            - 502 if backend service is unavailable
    """
    user_id, jwt_token = user_data

    logger.info(
        "Fetching liked movies for user",
        user_id=user_id,
        page=page,
        limit=limit,
        service="bff",
        endpoint="liked_movies",
    )

    try:
        ***REMOVED*** Get liked movies interactions from backend (using the same pattern as watched)
        ***REMOVED*** Decorators handle errors automatically
        liked_interactions_response = await _get_user_liked_movies(
            backend=backend,
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            page=page,
        )

        ***REMOVED*** The backend client now returns fast-core format with {"results": [...]} format
        ***REMOVED*** Extract the collection items from the liked-movies collection endpoint
        liked_collection_items: List[Dict[str, Any]] = liked_interactions_response.get(
            "results", []
        )

        ***REMOVED*** All items from the liked-movies collection are liked by definition
        ***REMOVED*** No need to filter - these are already the liked movies
        actually_liked = liked_collection_items

        if not actually_liked:
            logger.info(
                "No liked movies found for user",
                user_id=user_id,
                service="bff",
                endpoint="liked_movies",
            )
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
                    "collection_type": "liked_movies",
                    "user_context": {"user_id": user_id},
                },
            )
            return cast(Dict[str, Any], response)

        ***REMOVED*** Extract movie IDs for bulk fetching - collection items have movie_id directly
        valid_movie_ids = [
            item["movie_id"] for item in actually_liked if item.get("movie_id") is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.info(
                "No valid movie IDs found in liked interactions",
                user_id=user_id,
                service="bff",
                endpoint="liked_movies",
            )
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
                    "collection_type": "liked_movies",
                    "user_context": {"user_id": user_id},
                    "error": "No valid movie IDs found",
                },
            )
            return cast(Dict[str, Any], response)

        ***REMOVED*** Fetch movie details in bulk
        ***REMOVED*** Decorator handles errors automatically, but we can still catch for graceful fallback
        try:
            movies_response = await _get_movies_bulk(
                backend=backend,
                movie_ids=movie_ids,
                user_id=user_id,
                page=1,  ***REMOVED*** Get all movies in one request since we already paginated the interactions
                limit=len(movie_ids),  ***REMOVED*** Get all movies
            )
            movies_data = movies_response.get("results", [])
        except Exception:
            ***REMOVED*** Graceful fallback - decorator already logged the error
            movies_data = []

        ***REMOVED*** Create a mapping of movie_id to collection item data for efficient lookup
        collection_item_map = {
            item["movie_id"]: item for item in actually_liked if item.get("movie_id")
        }

        ***REMOVED*** Merge movie details with collection item data
        enriched_movies: List[Dict[str, Any]] = []
        for movie in movies_data:
            movie_id = movie.get("id")
            if movie_id and movie_id in collection_item_map:
                collection_item = collection_item_map[movie_id]

                ***REMOVED*** Merge collection item data with movie details
                enriched_movie = {**movie}

                ***REMOVED*** Set the frontend-expected interaction fields for liked movies
                enriched_movie["watched"] = (
                    False  ***REMOVED*** Unknown from collection data, would need separate lookup
                )
                enriched_movie["liked"] = True  ***REMOVED*** Always true since this is from liked collection
                enriched_movie["in_watchlist"] = (
                    False  ***REMOVED*** Unknown from collection data, would need separate lookup
                )

                ***REMOVED*** Ensure user_interactions object is present with complete structure
                enriched_movie["user_interactions"] = {
                    "in_watchlist": False,  ***REMOVED*** Unknown from collection data
                    "is_favorite": True,  ***REMOVED*** Always true for liked movies
                    "user_rating": None,  ***REMOVED*** Unknown from collection data
                    "watch_progress": 0,  ***REMOVED*** Unknown from collection data
                    "is_watched": False,  ***REMOVED*** Unknown from collection data
                    "liked_at": collection_item.get("added_at"),  ***REMOVED*** Use added_at as liked_at
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
        backend_pagination = liked_interactions_response.get("pagination", {})
        total_count = backend_pagination.get("total", len(enriched_movies))
        has_next = backend_pagination.get("has_next", len(actually_liked) == limit)
        has_prev = backend_pagination.get("has_prev", page > 1)
        total_pages = backend_pagination.get("total_pages", 1)

        logger.info(
            "Returning liked movies for user",
            user_id=user_id,
            returned_count=len(enriched_movies),
            interaction_count=len(actually_liked),
            service="bff",
            endpoint="liked_movies",
        )

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
                "collection_type": "liked_movies",
                "user_context": {"user_id": user_id},
                "collection_stats": {
                    "total_liked": total_count,
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
            "Backend service error for liked movies",
            error=str(e),
            service="bff",
            endpoint="liked_movies",
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
            "Internal error processing liked movies request",
            error=str(e),
            service="bff",
            endpoint="liked_movies",
            user_id=user_id,
            exc_info=True,  ***REMOVED*** Include stack trace for debugging
        )
        ***REMOVED*** Return 500 for internal errors (bugs in our code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        )
