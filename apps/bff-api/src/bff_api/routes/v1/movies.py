"""Movie-related routes for BFF API."""

import json
from typing import Any, Dict, List, Optional, Union, cast

from cache.decorators import redis_cache
from cache.keys import build_cache_key, build_filtered_key
from config.logging import get_logger
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_api.dependencies.common import get_backend_client
from bff_api.schemas.screen_schemas import MovieListData, MovieScreenData, UserInteractions
from bff_api.services.backend_client import BackendClient, BackendClientError
from bff_api.utils.auth import extract_user_id_from_token

logger = get_logger(__name__)
router = APIRouter(tags=["movies"])

***REMOVED*** Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


def _build_movies_list_cache_key(
    page: int,
    limit: int,
    genre_id: Optional[int],
    actor_id: Optional[int],
    sort_by: Optional[str],
    sort_desc: Optional[bool],
    imdb_rating: Optional[float],
    rotten_tomatoes_rating: Optional[int],
    metacritic_rating: Optional[int],
    year: Optional[int],
    start_year: Optional[int],
    end_year: Optional[int],
    user_id: Optional[int],
    backend: BackendClient,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> str:
    """Build cache key for movies list with all parameters using cache library utilities."""
    filters = {
        "page": page,
        "limit": limit,
        "genre_id": genre_id,
        "actor_id": actor_id,
        "sort_by": sort_by,
        "sort_desc": sort_desc,
        "imdb_rating": imdb_rating,
        "rotten_tomatoes_rating": rotten_tomatoes_rating,
        "metacritic_rating": metacritic_rating,
        "year": year,
        "start_year": start_year,
        "end_year": end_year,
    }
    return build_filtered_key("screen:movies", "list", filters, user_id=user_id, prefix="")


@redis_cache(
    ttl=1800,  ***REMOVED*** 30 minutes for user-specific, 1 hour for anonymous
    key_builder=lambda movie_id, user_id, backend, credentials=None: build_cache_key(
        "screen:movie", [movie_id, "user", user_id or "anon"], prefix=""
    ),
)
async def _get_movie_screen_data(
    movie_id: int,
    user_id: Optional[int],
    backend: BackendClient,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> Dict[str, Any]:
    """Internal cached function for movie screen aggregation."""
    logger.info(
        "Building movie screen data",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="screen_data",
    )

    ***REMOVED*** Fetch all data from backend (backend will handle its own caching)
    logger.info("Fetching movie details from backend", movie_id=movie_id, service="bff")
    movie = await backend.get_movie(movie_id, user_id=user_id)

    logger.info("Fetching movie cast from backend", movie_id=movie_id, service="bff")
    movie_cast = await backend.get_movie_cast(movie_id)

    logger.info("Fetching movie trailers from backend", movie_id=movie_id, service="bff")
    trailers = await backend.get_movie_trailers(movie_id)

    logger.info("Fetching similar movies from backend", movie_id=movie_id, service="bff")
    similar_movies = await backend.get_similar_movies(
        movie_id,
        limit=20,
        min_score=0.01,
    )

    ***REMOVED*** Enrich similar movies with full details and user interactions
    if similar_movies:
        ***REMOVED*** Extract movie IDs for bulk fetching
        similar_movie_ids: List[int] = []
        for similar_item in similar_movies:
            movie_id_value = similar_item.get("id")
            if movie_id_value is not None and isinstance(movie_id_value, (int, str)):
                try:
                    similar_movie_ids.append(int(movie_id_value))
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid movie ID in similar movies",
                        invalid_id=movie_id_value,
                        service="bff",
                        component="similar_movies",
                    )

        if similar_movie_ids:
            try:
                ***REMOVED*** Fetch movie details in bulk
                movies_response = await backend.get_movies_bulk(
                    movie_ids=similar_movie_ids,
                    user_id=user_id,
                    page=1,
                    limit=len(similar_movie_ids),
                )
                similar_movies = movies_response.get("results", [])

                ***REMOVED*** Add user interactions for authenticated users
                if user_id and credentials:
                    for similar_movie in similar_movies:
                        similar_movie_id = similar_movie.get("id")
                        if similar_movie_id:
                            try:
                                interaction_data = await backend.get_user_movie_interaction(
                                    user_id, similar_movie_id, jwt_token=credentials.credentials
                                )
                                if interaction_data:
                                    similar_movie["liked"] = interaction_data.get("liked", False)
                                    similar_movie["watched"] = interaction_data.get(
                                        "watched", False
                                    )
                                    similar_movie["in_watchlist"] = interaction_data.get(
                                        "in_watchlist", False
                                    )
                                    similar_movie["user_interactions"] = {
                                        "in_watchlist": interaction_data.get("in_watchlist", False),
                                        "is_favorite": interaction_data.get("liked", False),
                                        "user_rating": interaction_data.get("rating"),
                                        "watch_progress": interaction_data.get("watch_progress", 0),
                                        "is_watched": interaction_data.get("watched", False),
                                    }
                                else:
                                    ***REMOVED*** Set default values
                                    similar_movie["liked"] = False
                                    similar_movie["watched"] = False
                                    similar_movie["in_watchlist"] = False
                                    similar_movie["user_interactions"] = {
                                        "in_watchlist": False,
                                        "is_favorite": False,
                                        "user_rating": None,
                                        "watch_progress": 0,
                                        "is_watched": False,
                                    }
                            except Exception as e:
                                logger.warning(
                                    "Failed to get user interaction for similar movie",
                                    similar_movie_id=similar_movie_id,
                                    error=str(e),
                                    service="bff",
                                )
                                ***REMOVED*** Set default values on error
                                similar_movie["liked"] = False
                                similar_movie["watched"] = False
                                similar_movie["in_watchlist"] = False
                                similar_movie["user_interactions"] = {
                                    "in_watchlist": False,
                                    "is_favorite": False,
                                    "user_rating": None,
                                    "watch_progress": 0,
                                    "is_watched": False,
                                }
                else:
                    ***REMOVED*** For anonymous users, set all interaction fields to false
                    for similar_movie in similar_movies:
                        similar_movie["liked"] = False
                        similar_movie["watched"] = False
                        similar_movie["in_watchlist"] = False
                        similar_movie["user_interactions"] = {
                            "in_watchlist": False,
                            "is_favorite": False,
                            "user_rating": None,
                            "watch_progress": 0,
                            "is_watched": False,
                        }
            except Exception as e:
                logger.warning(
                    "Failed to enrich similar movies",
                    error=str(e),
                    service="bff",
                    component="similar_movies",
                )

    ***REMOVED*** Get user interactions for the main movie
    user_interactions_dict: Dict[str, Any] = {
        "in_watchlist": False,
        "is_favorite": False,
        "user_rating": None,
        "watch_progress": 0,
        "is_watched": False,
    }

    if user_id and credentials:
        try:
            interaction_data = await backend.get_user_movie_interaction(
                user_id, movie_id, jwt_token=credentials.credentials
            )
            if interaction_data:
                user_interactions_dict = {
                    "in_watchlist": interaction_data.get("in_watchlist", False),
                    "is_favorite": interaction_data.get("liked", False),
                    "user_rating": interaction_data.get("rating"),
                    "watch_progress": interaction_data.get("watch_progress", 0),
                    "is_watched": interaction_data.get("watched", False),
                }
        except Exception as e:
            logger.warning(
                "Failed to get user interactions",
                user_id=user_id,
                movie_id=movie_id,
                error=str(e),
                service="bff",
            )

    ***REMOVED*** Build the complete screen response as a dictionary for caching
    screen_data = {
        "movie": movie,
        "cast": movie_cast,
        "trailers": trailers,
        "similar_movies": similar_movies,
        "user_interactions": user_interactions_dict,
    }

    logger.info(
        "Successfully built movie screen data",
        movie_id=movie_id,
        user_id=user_id,
        service="bff",
        component="screen_data",
    )

    return screen_data


@router.get("/movies/{movie_id}", response_model=MovieScreenData)
async def get_movie_screen(
    movie_id: int = Path(..., description="Movie ID"),
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> MovieScreenData:
    """Get aggregated data for movie detail screen.

    Fetches complete movie information including cast, similar movies,
    and user-specific interaction data for the movie detail view.

    Args:
        movie_id: Movie ID to fetch details for
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Aggregated movie detail screen data

    Raises:
        HTTPException: 404 if movie not found, 502 if backend unavailable
    """
    ***REMOVED*** Extract user ID from JWT token if provided
    user_id = None
    logger.info(
        "Processing movie detail request",
        movie_id=movie_id,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="movie_detail",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.info(
            "User authenticated for movie detail",
            movie_id=movie_id,
            user_id=user_id,
            service="bff",
            endpoint="movie_detail",
        )
    else:
        logger.info(
            "Anonymous user accessing movie detail",
            movie_id=movie_id,
            service="bff",
            endpoint="movie_detail",
        )

    try:
        ***REMOVED*** Use the cached function - decorator handles all cache logic
        screen_data_dict = await _get_movie_screen_data(movie_id, user_id, backend, credentials)

        ***REMOVED*** Convert dictionary back to Pydantic model
        return MovieScreenData(**screen_data_dict)

    except BackendClientError as e:
        logger.error(
            "Backend error for movie detail",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            endpoint="movie_detail",
        )
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Movie not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
    except Exception as e:
        logger.error(
            "Unexpected error in movie detail endpoint",
            movie_id=movie_id,
            error=str(e),
            service="bff",
            endpoint="movie_detail",
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@redis_cache(
    ttl=900,  ***REMOVED*** 15 minutes for user-specific, 30 minutes for anonymous
    key_builder=_build_movies_list_cache_key,
)
async def _get_movies_list_data(
    page: int,
    limit: int,
    genre_id: Optional[int],
    actor_id: Optional[int],
    sort_by: Optional[str],
    sort_desc: Optional[bool],
    imdb_rating: Optional[float],
    rotten_tomatoes_rating: Optional[int],
    metacritic_rating: Optional[int],
    year: Optional[int],
    start_year: Optional[int],
    end_year: Optional[int],
    user_id: Optional[int],
    backend: BackendClient,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> Dict[str, Any]:
    """Internal cached function for movies list aggregation."""
    logger.info(
        "Building movies list data",
        page=page,
        limit=limit,
        user_id=user_id,
        service="bff",
        component="list_data",
    )

    ***REMOVED*** Build filter parameters
    kwargs: Dict[str, Any] = {"page": page, "limit": limit}

    ***REMOVED*** Add user_id if provided
    if user_id is not None:
        kwargs["user_id"] = user_id

    ***REMOVED*** Add optional filters
    if genre_id is not None:
        kwargs["genre_id"] = genre_id
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

    ***REMOVED*** Get movies from backend
    movies_response = await backend.get_movies(**kwargs)

    ***REMOVED*** Extract pagination data from backend's standardized format
    movies = movies_response.get("results", [])
    total_count = movies_response.get("total", 0)
    current_page = movies_response.get("page", page)
    per_page = movies_response.get("per_page", limit)
    total_pages = movies_response.get("total_pages", 0)
    has_next = movies_response.get("has_next", False)
    has_prev = movies_response.get("has_prev", False)

    ***REMOVED*** If user is authenticated, fetch user interactions for each movie
    if user_id and credentials:
        logger.info(
            "Fetching user interactions for movies list",
            user_id=user_id,
            movie_count=len(movies),
            service="bff",
            component="user_interactions",
        )
        for list_movie in movies:
            list_movie_id = list_movie.get("id")
            if list_movie_id:
                try:
                    interaction_data = await backend.get_user_movie_interaction(
                        user_id, list_movie_id, jwt_token=credentials.credentials
                    )
                    if interaction_data:
                        ***REMOVED*** Map user interaction data directly to movie fields
                        list_movie["liked"] = interaction_data.get("liked", False)
                        list_movie["watched"] = interaction_data.get("watched", False)
                        list_movie["in_watchlist"] = interaction_data.get("in_watchlist", False)

                        ***REMOVED*** Also include complete user_interactions object for reference
                        list_movie["user_interactions"] = {
                            "in_watchlist": interaction_data.get("in_watchlist", False),
                            "is_favorite": interaction_data.get("liked", False),
                            "user_rating": interaction_data.get("rating"),
                            "watch_progress": interaction_data.get("watch_progress", 0),
                            "is_watched": interaction_data.get("watched", False),
                        }
                    else:
                        ***REMOVED*** Set default values if no interaction data exists
                        list_movie["liked"] = False
                        list_movie["watched"] = False
                        list_movie["in_watchlist"] = False
                        list_movie["user_interactions"] = {
                            "in_watchlist": False,
                            "is_favorite": False,
                            "user_rating": None,
                            "watch_progress": 0,
                            "is_watched": False,
                        }
                except Exception as e:
                    logger.warning(
                        "Failed to get user interaction for movie in list",
                        movie_id=list_movie_id,
                        user_id=user_id,
                        error=str(e),
                        service="bff",
                        component="user_interactions",
                    )
                    ***REMOVED*** Set default values if fetching interaction data fails
                    list_movie["liked"] = False
                    list_movie["watched"] = False
                    list_movie["in_watchlist"] = False
                    list_movie["user_interactions"] = {
                        "in_watchlist": False,
                        "is_favorite": False,
                        "user_rating": None,
                        "watch_progress": 0,
                        "is_watched": False,
                    }
    else:
        ***REMOVED*** For anonymous users, set all interaction fields to false
        logger.info(
            "Setting default interaction values for anonymous user",
            movie_count=len(movies),
            service="bff",
            component="user_interactions",
        )
        for list_movie in movies:
            list_movie["liked"] = False
            list_movie["watched"] = False
            list_movie["in_watchlist"] = False
            list_movie["user_interactions"] = {
                "in_watchlist": False,
                "is_favorite": False,
                "user_rating": None,
                "watch_progress": 0,
                "is_watched": False,
            }

    ***REMOVED*** Build the complete movies list response as a dictionary for caching
    list_data = {
        "total": total_count,
        "page": current_page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "results": movies,
    }

    logger.info(
        "Successfully built movies list data",
        page=page,
        limit=limit,
        user_id=user_id,
        total_movies=len(movies),
        service="bff",
        component="list_data",
    )

    return list_data


@router.get("/movies", response_model=MovieListData)
async def get_movies_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
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
    backend: BackendClient = Depends(get_backend_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> MovieListData:
    """Get paginated list of movies with filters.

    Provides paginated movie listings with support for filtering by genre,
    actor, ratings, release year, and sorting by various criteria with
    user personalization.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        genre_id: Optional genre filter
        actor_id: Optional actor TMDB ID filter
        sort_by: Sort field (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)
        sort_desc: Sort in descending order
        imdb_rating: Minimum IMDb rating filter
        rotten_tomatoes_rating: Minimum Rotten Tomatoes rating filter
        metacritic_rating: Minimum Metacritic rating filter
        year: Release year filter
        start_year: Start release year filter (inclusive)
        end_year: End release year filter (inclusive)
        backend: Backend client dependency
        credentials: Optional Bearer token for authentication

    Returns:
        Paginated movie list with metadata

    Raises:
        HTTPException: If backend service is unavailable (502)
    """
    ***REMOVED*** Extract user ID from JWT token if provided
    user_id = None
    logger.info(
        "Processing movies list request",
        page=page,
        limit=limit,
        has_credentials=bool(credentials),
        service="bff",
        endpoint="movies_list",
    )

    if credentials and credentials.credentials:
        user_id = extract_user_id_from_token(credentials.credentials)
        logger.info(
            "User authenticated for movies list",
            user_id=user_id,
            service="bff",
            endpoint="movies_list",
        )
    else:
        logger.info("Anonymous user accessing movies list", service="bff", endpoint="movies_list")

    try:
        ***REMOVED*** Use the cached function - decorator handles all cache logic
        list_data_dict = await _get_movies_list_data(
            page=page,
            limit=limit,
            genre_id=genre_id,
            actor_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
            user_id=user_id,
            backend=backend,
            credentials=credentials,
        )

        ***REMOVED*** Convert dictionary back to Pydantic model
        return MovieListData(**list_data_dict)

    except BackendClientError as e:
        logger.error(
            "Backend error for movies list", error=str(e), service="bff", endpoint="movies_list"
        )
        raise HTTPException(status_code=502, detail="Backend service unavailable")
