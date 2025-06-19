"""Liked movies-related routes for BFF API."""

from typing import Any, Dict, List, Optional, cast

from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Query

from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.dependencies.common import get_backend_client
from bff_api.schemas.screen_schemas import MovieListData
from bff_api.services.backend_client import BackendClient, BackendClientError

logger = get_logger(__name__)
router = APIRouter(tags=["liked"])


@router.get("/liked", response_model=MovieListData)
async def get_user_liked_movies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    ***REMOVED*** Filter parameters
    imdb_rating: float = Query(None, ge=0, le=10, description="Minimum IMDb rating"),
    rotten_tomatoes_rating: float = Query(
        None, ge=0, le=100, description="Minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: float = Query(None, ge=0, le=100, description="Minimum Metacritic rating"),
    year: int = Query(None, ge=1900, le=2030, description="Release year"),
    sort_by: str = Query(
        "title",
        description="Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieListData:
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
        backend: Backend service client

    Returns:
        Paginated list of liked movies with full details and user interactions

    Raises:
        HTTPException:
            - 401 if not authenticated
            - 502 if backend service is unavailable
    """
    user_id, jwt_token = user_data

    ***REMOVED*** Calculate offset for pagination
    offset = (page - 1) * limit

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
        liked_interactions_response = await backend.get_user_liked_movies(
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            offset=offset,
        )

        ***REMOVED*** The backend client wraps list responses in {"data": [...]} format
        ***REMOVED*** Extract the interactions list from the wrapped response
        liked_interactions: List[Dict[str, Any]] = liked_interactions_response.get("data", [])

        ***REMOVED*** Filter to only get actually liked movies (since some interactions might have liked=false)
        actually_liked = [
            interaction for interaction in liked_interactions if interaction.get("liked", False)
        ]

        if not actually_liked:
            logger.info(
                "No liked movies found for user",
                user_id=user_id,
                service="bff",
                endpoint="liked_movies",
            )
            return MovieListData(
                total=0,
                page=page,
                per_page=limit,
                total_pages=0,
                has_next=False,
                has_prev=False,
                results=[],
            )

        ***REMOVED*** Extract movie IDs for bulk fetching - filter out None values first and then convert to int
        valid_movie_ids = [
            mid
            for mid in [interaction.get("movie_id") for interaction in actually_liked]
            if mid is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.info(
                "No valid movie IDs found in liked interactions",
                user_id=user_id,
                service="bff",
                endpoint="liked_movies",
            )
            return MovieListData(
                total=0,
                page=page,
                per_page=limit,
                total_pages=0,
                has_next=False,
                has_prev=False,
                results=[],
            )

        ***REMOVED*** Fetch movie details in bulk
        try:
            movies_response = await backend.get_movies_bulk(
                movie_ids=movie_ids,
                user_id=user_id,
                page=1,  ***REMOVED*** Get all movies in one request since we already paginated the interactions
                limit=len(movie_ids),  ***REMOVED*** Get all movies
            )

            movies_data = movies_response.get("results", [])

        except Exception as e:
            logger.error(
                "Failed to fetch bulk movie details for liked movies",
                user_id=user_id,
                error=str(e),
                service="bff",
                endpoint="liked_movies",
            )
            ***REMOVED*** Fallback to empty response instead of failing completely
            movies_data = []

        ***REMOVED*** Create a mapping of movie_id to interaction data for efficient lookup
        interaction_map = {
            interaction.get("movie_id"): interaction
            for interaction in actually_liked
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
                enriched_movie["liked"] = interaction.get(
                    "liked", True
                )  ***REMOVED*** Always true for liked movies
                enriched_movie["in_watchlist"] = interaction.get("in_watchlist", False)

                ***REMOVED*** Ensure user_interactions object is present with complete structure
                enriched_movie["user_interactions"] = {
                    "in_watchlist": interaction.get("in_watchlist", False),
                    "is_favorite": interaction.get("liked", True),  ***REMOVED*** Always true for liked movies
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
            len(actually_liked) == limit
        )  ***REMOVED*** If we got a full page of interactions, assume there might be more
        has_prev = page > 1
        total_pages = page if not has_next else page + 1  ***REMOVED*** Estimate based on current page

        logger.info(
            "Returning liked movies for user",
            user_id=user_id,
            returned_count=len(enriched_movies),
            interaction_count=len(actually_liked),
            service="bff",
            endpoint="liked_movies",
        )

        return MovieListData(
            total=total_count,
            page=page,
            per_page=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            results=enriched_movies,
        )

    except BackendClientError as e:
        logger.error(
            "Backend error fetching liked movies",
            user_id=user_id,
            error=str(e),
            service="bff",
            endpoint="liked_movies",
        )
        if "401" in str(e):
            raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            raise HTTPException(status_code=502, detail="Backend service unavailable")
