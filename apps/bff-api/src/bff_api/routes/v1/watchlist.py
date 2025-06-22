"""Watchlist movies-related routes for BFF API."""

from typing import Any, Dict, List, Optional, Union, cast

import httpx
from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies import get_backend_client
from fast_core.responses import ResponseBuilder

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


async def _get_user_watchlist(
    backend: httpx.AsyncClient,
    user_id: int,
    jwt_token: str,
    limit: int,
    offset: int,
) -> Dict[str, Any]:
    """Get user's watchlist interactions from backend.

    Args:
        backend: HTTP client for backend service
        user_id: User ID
        jwt_token: JWT token for authentication
        limit: Number of items to fetch
        offset: Offset for pagination

    Returns:
        Watchlist interactions response

    Raises:
        httpx.HTTPStatusError: If HTTP request fails
        httpx.RequestError: If request cannot be made
    """
    response = await backend.get(
        _build_api_path(f"/users/{user_id}/interactions/watchlist"),
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    response.raise_for_status()
    result: Dict[str, Any] = response.json()
    return result


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
    response = await backend.post(
        _build_api_path("/movies/bulk"),
        json={"movie_ids": movie_ids},
        params={"user_id": user_id, "page": page, "limit": limit},
    )
    response.raise_for_status()
    result: Dict[str, Any] = response.json()
    return result


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
    backend: httpx.AsyncClient = Depends(get_backend_client),
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
    user_id, jwt_token = user_data

    ***REMOVED*** Calculate offset for pagination
    offset = (page - 1) * limit

    logger.info(f"📋 Fetching watchlist for user {user_id} (page {page}, limit {limit})")

    try:
        ***REMOVED*** Get watchlist interactions from backend (using the same pattern as watched)
        watchlist_interactions_response = await _get_user_watchlist(
            backend=backend,
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            offset=offset,
        )

        ***REMOVED*** The backend client wraps list responses in {"data": [...]} format
        ***REMOVED*** Extract the interactions list from the wrapped response
        watchlist_interactions: List[Dict[str, Any]] = watchlist_interactions_response.get(
            "data", []
        )

        ***REMOVED*** Filter to only get actually watchlisted movies (since some interactions might have in_watchlist=false)
        actually_watchlisted = [
            interaction
            for interaction in watchlist_interactions
            if interaction.get("in_watchlist", False)
        ]

        if not actually_watchlisted:
            logger.info(f"No watchlist movies found for user {user_id}")
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
            logger.info(f"No valid movie IDs found in watchlist interactions for user {user_id}")
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

        ***REMOVED*** Calculate pagination metadata based on the filtered results
        total_count = len(enriched_movies)
        has_next = (
            len(actually_watchlisted) == limit
        )  ***REMOVED*** If we got a full page of interactions, assume there might be more
        has_prev = page > 1
        total_pages = page if not has_next else page + 1  ***REMOVED*** Estimate based on current page

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
                    "total_watchlisted": len(actually_watchlisted),
                    "filtered_count": len(enriched_movies),
                },
            },
        )
        return cast(Dict[str, Any], response)

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        await _handle_backend_error(e, "watchlist_movies", user_id=user_id)
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
                "collection_type": "watchlist_movies",
                "user_context": {"user_id": user_id},
            },
        )
        return cast(Dict[str, Any], response)
