"""Watched movies routes for BFF API."""

import logging
from typing import Optional, List, Dict, Any, cast
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bff_api.schemas.screen_schemas import MovieListData
from bff_api.dependencies.common import get_backend_client
from bff_api.dependencies.auth import get_current_user_id_and_token
from bff_api.services.backend_client import BackendClient, BackendClientError

from bff_api.config.logging import get_logger

logger = get_logger("bff_api.routes.watched")
router = APIRouter(tags=["watched"])


@router.get("/watched", response_model=MovieListData)
async def get_watched_movies(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_data: tuple[int, str] = Depends(get_current_user_id_and_token),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieListData:
    """Get user's watched movies.

    Provides a paginated list of movies that the authenticated user has marked
    as watched, including their interaction data and movie details.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        user_data: Authenticated user ID and JWT token
        backend: Backend client dependency

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
        watched_interactions_response = await backend.get_user_watched_movies(
            user_id=user_id,
            jwt_token=jwt_token,
            limit=limit,
            offset=offset,
        )

        ***REMOVED*** The backend returns a list of user interaction objects
        watched_interactions: List[Dict[str, Any]] = (
            watched_interactions_response if isinstance(watched_interactions_response, list) else []
        )

        ***REMOVED*** Filter to only get actually watched movies (since some interactions might have watched=false)
        actually_watched = [
            interaction for interaction in watched_interactions if interaction.get("watched", False)
        ]

        if not actually_watched:
            logger.info(f"No watched movies found for user {user_id}")
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
            for mid in [interaction.get("movie_id") for interaction in actually_watched]
            if mid is not None
        ]
        movie_ids = [int(mid) for mid in valid_movie_ids]

        if not movie_ids:
            logger.info(f"No valid movie IDs found in watched interactions for user {user_id}")
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
        logger.error(f"Backend error fetching watched movies for user {user_id}: {e}")
        if "401" in str(e):
            raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            raise HTTPException(status_code=502, detail="Backend service unavailable")
