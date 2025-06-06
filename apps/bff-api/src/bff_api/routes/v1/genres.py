"""Genre-related routes for BFF API."""

import logging
from typing import Optional, Dict, Any, Union, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bff_api.schemas.screen_schemas import GenreScreenData
from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError
from bff_api.utils.auth import extract_user_id_from_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["genres"])

***REMOVED*** Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


@router.get("/genres/{genre_id}", response_model=GenreScreenData)
async def get_genre_screen(
    genre_id: int = Path(..., description="Genre ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: Optional[str] = Query(
        None,
        description="Sort by field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: Optional[bool] = Query(True, description="Sort in descending order"),
    imdb_rating: Optional[float] = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: Optional[int] = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: Optional[int] = Query(None, description="Filter by release year"),
    start_year: Optional[int] = Query(None, description="Filter by start year (inclusive)"),
    end_year: Optional[int] = Query(None, description="Filter by end year (inclusive)"),
    user_id: Optional[int] = Query(None, description="User ID for personalized content"),
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> GenreScreenData:
    """Get aggregated data for genre screen.

    Provides movies filtered by specific genre with pagination support,
    additional filtering by actor, ratings, release year, and sorting
    options with optional user personalization.

    Args:
        genre_id: Genre ID to filter movies by
        page: Page number for pagination
        limit: Number of items per page
        actor_id: Optional actor TMDB ID for filtering
        sort_by: Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        sort_desc: Sort in descending order
        imdb_rating: Minimum IMDb rating filter
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating filter
        metacritic_rating: Minimum Metacritic rating filter
        year: Release year filter
        start_year: Start release year filter (inclusive)
        end_year: End release year filter (inclusive)
        user_id: Optional user ID for personalized content (deprecated - use JWT token)
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Aggregated genre screen data with movies and metadata

    Raises:
        HTTPException: 404 if genre not found, 502 if backend unavailable
    """
    ***REMOVED*** Extract user ID from JWT token if provided (overrides query parameter)
    extracted_user_id = None
    logger.info(f"🔍 Debugging token extraction for genre {genre_id}")
    logger.info(f"📋 Credentials present: {bool(credentials)}")

    if credentials and credentials.credentials:
        logger.info(f"🔑 Token present: {bool(credentials.credentials)}")
        logger.info(f"🔑 Token preview: {credentials.credentials[:20]}...")

        ***REMOVED*** Temporarily enable debug logging for JWT extraction
        auth_logger = logging.getLogger("bff_api.utils.auth")
        original_level = auth_logger.level
        auth_logger.setLevel(logging.DEBUG)

        extracted_user_id = extract_user_id_from_token(credentials.credentials)

        ***REMOVED*** Restore original logging level
        auth_logger.setLevel(original_level)

        logger.info(f"👤 Extracted user_id: {extracted_user_id}")
    else:
        logger.info("❌ No credentials or token found - treating as anonymous user")

    ***REMOVED*** Use extracted user ID from token, fallback to query parameter
    final_user_id = extracted_user_id or user_id

    try:
        ***REMOVED*** Get genre details from backend
        try:
            genre_response = await backend.get_genre(genre_id)
            logger.info(f"Retrieved genre {genre_id}: {genre_response}")
        except BackendClientError as e:
            if "404" in str(e):
                raise HTTPException(status_code=404, detail="Genre not found")
            logger.error(f"Failed to get genre {genre_id}: {e}")
            raise HTTPException(status_code=502, detail="Backend service unavailable")

        ***REMOVED*** Get movies for this genre with filters
        kwargs: Dict[str, Any] = {"genre_id": genre_id}
        if actor_id is not None:
            kwargs["actor_id"] = actor_id
        if sort_by is not None:
            kwargs["sort_by"] = sort_by
        if sort_desc is not None:
            kwargs["sort_desc"] = sort_desc
        if imdb_rating is not None:
            kwargs["imdb_rating"] = imdb_rating
        if rotten_tomatoes_rating is not None:
            kwargs["rotten_tomatoes_rating"] = rotten_tomatoes_rating
        if metacritic_rating is not None:
            kwargs["metacritic_rating"] = metacritic_rating
        if year is not None:
            kwargs["year"] = year
        if start_year is not None:
            kwargs["start_year"] = start_year
        if end_year is not None:
            kwargs["end_year"] = end_year

        movies_response = await backend.get_movies(
            page=page,
            limit=limit,
            user_id=final_user_id,
            **kwargs,
        )

        ***REMOVED*** Extract pagination data from backend's standardized format
        movies = movies_response.get("results", [])
        total_count = movies_response.get("total", 0)
        current_page = movies_response.get("page", page)
        per_page = movies_response.get("per_page", limit)
        total_pages = movies_response.get("total_pages", 0)
        has_next = movies_response.get("has_next", False)
        has_prev = movies_response.get("has_prev", False)

        ***REMOVED*** If user is authenticated, fetch user interactions for each movie
        if final_user_id and credentials:
            logger.info(f"🔄 Fetching user interactions for {len(movies)} movies")
            for movie in movies:
                movie_id = movie.get("id")
                if movie_id:
                    try:
                        interaction_data = await backend.get_user_movie_interaction(
                            final_user_id, movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            ***REMOVED*** Map user interaction data directly to movie fields
                            movie["liked"] = interaction_data.get("liked", False)
                            movie["watched"] = interaction_data.get("watched", False)
                            movie["in_watchlist"] = interaction_data.get("in_watchlist", False)
                            movie["user_interactions"] = {
                                "in_watchlist": interaction_data.get("in_watchlist", False),
                                "is_favorite": interaction_data.get("liked", False),
                                "user_rating": interaction_data.get("rating"),
                                "watch_progress": interaction_data.get("watch_progress", 0),
                                "is_watched": interaction_data.get("watched", False),
                            }
                        else:
                            ***REMOVED*** Set default values if no interaction data exists
                            movie["liked"] = False
                            movie["watched"] = False
                            movie["in_watchlist"] = False
                            movie["user_interactions"] = {
                                "in_watchlist": False,
                                "is_favorite": False,
                                "user_rating": None,
                                "watch_progress": 0,
                                "is_watched": False,
                            }
                    except Exception as e:
                        logger.warning(f"Failed to get user interaction for movie {movie_id}: {e}")
                        ***REMOVED*** Set default values if fetching interaction data fails
                        movie["liked"] = False
                        movie["watched"] = False
                        movie["in_watchlist"] = False
                        movie["user_interactions"] = {
                            "in_watchlist": False,
                            "is_favorite": False,
                            "user_rating": None,
                            "watch_progress": 0,
                            "is_watched": False,
                        }
        else:
            ***REMOVED*** For anonymous users, set all interaction fields to false
            logger.info("No user authenticated - setting default interaction values")
            for movie in movies:
                movie["liked"] = False
                movie["watched"] = False
                movie["in_watchlist"] = False
                movie["user_interactions"] = {
                    "in_watchlist": False,
                    "is_favorite": False,
                    "user_rating": None,
                    "watch_progress": 0,
                    "is_watched": False,
                }

        return GenreScreenData(
            genre=genre_response,
            total=total_count,
            page=current_page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            results=movies,
        )

    except BackendClientError as e:
        logger.error(f"Backend error for genre {genre_id}: {e}")
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Genre not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
