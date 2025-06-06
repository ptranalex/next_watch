"""Movie-related routes for BFF API."""

import logging
from typing import Dict, List, Any, Optional, Union, cast
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from bff_api.schemas.screen_schemas import MovieScreenData, MovieListData, UserInteractions
from bff_api.dependencies.common import get_backend_client
from bff_api.services.backend_client import BackendClient, BackendClientError
from bff_api.utils.auth import extract_user_id_from_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["movies"])

***REMOVED*** Security scheme for optional authentication
security = HTTPBearer(auto_error=False)


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
    logger.info(f"🔍 Debugging token extraction for movie {movie_id}")
    logger.info(f"📋 Credentials present: {bool(credentials)}")

    if credentials and credentials.credentials:
        logger.info(f"🔑 Token present: {bool(credentials.credentials)}")
        logger.info(f"🔑 Token preview: {credentials.credentials[:20]}...")

        ***REMOVED*** Temporarily enable debug logging for JWT extraction
        auth_logger = logging.getLogger("bff_api.utils.auth")
        original_level = auth_logger.level
        auth_logger.setLevel(logging.DEBUG)

        user_id = extract_user_id_from_token(credentials.credentials)

        ***REMOVED*** Restore original logging level
        auth_logger.setLevel(original_level)

        logger.info(f"👤 Extracted user_id: {user_id}")
    else:
        logger.info("❌ No credentials or token found - treating as anonymous user")

    try:
        ***REMOVED*** Get movie details
        movie = await backend.get_movie(movie_id, user_id=user_id)

        ***REMOVED*** Get cast information
        try:
            cast = await backend.get_movie_cast(movie_id)
        except BackendClientError:
            logger.warning(f"Failed to get cast for movie {movie_id}")
            cast = []

        ***REMOVED*** Get trailers information
        try:
            trailers = await backend.get_movie_trailers(movie_id)
        except BackendClientError:
            logger.warning(f"Failed to get trailers for movie {movie_id}")
            trailers = []

        ***REMOVED*** Get similar movies from recommendation API
        try:
            similar_movies = await backend.get_similar_movies(
                movie_id,
                limit=20,  ***REMOVED*** Reduced from 20 to prevent database connection pool issues
                min_score=0.01,
            )
            logger.info(
                f"Successfully fetched {len(similar_movies)} similar movies for movie {movie_id}"
            )

            ***REMOVED*** Extract movie IDs for bulk fetching
            similar_movie_ids: List[int] = []
            for similar_item in similar_movies:
                movie_id_value = similar_item.get("id")
                if movie_id_value is not None and isinstance(movie_id_value, (int, str)):
                    try:
                        similar_movie_ids.append(int(movie_id_value))
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid movie ID in similar movies: {movie_id_value}")

            if similar_movie_ids:
                ***REMOVED*** Fetch movie details in bulk
                try:
                    movies_response = await backend.get_movies_bulk(
                        movie_ids=similar_movie_ids,
                        user_id=user_id,
                        page=1,  ***REMOVED*** Get all movies in one request
                        limit=len(similar_movie_ids),  ***REMOVED*** Get all movies
                    )

                    similar_movies = movies_response.get("results", [])
                    logger.info(
                        f"Successfully enriched {len(similar_movies)} similar movies with details"
                    )

                    ***REMOVED*** If user is authenticated, fetch user interactions for each similar movie
                    if user_id and credentials:
                        logger.info(f"Enriching similar movies with user interaction data")
                        for similar_movie in similar_movies:
                            similar_movie_id = similar_movie.get("id")
                            if similar_movie_id:
                                try:
                                    interaction_data = await backend.get_user_movie_interaction(
                                        user_id, similar_movie_id, jwt_token=credentials.credentials
                                    )
                                    if interaction_data:
                                        ***REMOVED*** Map user interaction data directly to movie fields for frontend compatibility
                                        similar_movie["liked"] = interaction_data.get(
                                            "liked", False
                                        )
                                        similar_movie["watched"] = interaction_data.get(
                                            "watched", False
                                        )
                                        similar_movie["in_watchlist"] = interaction_data.get(
                                            "in_watchlist", False
                                        )

                                        ***REMOVED*** Also include complete user_interactions object
                                        similar_movie["user_interactions"] = {
                                            "in_watchlist": interaction_data.get(
                                                "in_watchlist", False
                                            ),
                                            "is_favorite": interaction_data.get("liked", False),
                                            "user_rating": interaction_data.get("rating"),
                                            "watch_progress": interaction_data.get(
                                                "watch_progress", 0
                                            ),
                                            "is_watched": interaction_data.get("watched", False),
                                        }
                                    else:
                                        ***REMOVED*** Set default values if no interaction data exists
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
                                        f"Failed to get user interaction for similar movie {similar_movie_id}: {e}"
                                    )
                                    ***REMOVED*** Set default values if fetching interaction data fails
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
                except BackendClientError as e:
                    logger.warning(f"Failed to get bulk details for similar movies: {e}")
                    ***REMOVED*** Keep the original similar_movies if bulk fetch fails
            else:
                logger.warning("No valid movie IDs found in similar movies response")
        except BackendClientError as e:
            error_msg = str(e)
            if "QueuePool limit" in error_msg or "503" in error_msg:
                logger.error(
                    f"Database connection pool limit reached when fetching similar movies for movie {movie_id}: {e}"
                )
                ***REMOVED*** Return empty list for similar movies in case of connection pool errors
                similar_movies = []
            else:
                logger.warning(f"Failed to get similar movies for movie {movie_id}: {e}")
                similar_movies = []

        ***REMOVED*** User interactions (watchlist, favorite, rating)
        user_interactions_dict: Dict[str, Any] = {}
        if user_id and credentials:
            ***REMOVED*** Fetch real user interaction data
            try:
                interaction_data = await backend.get_user_movie_interaction(
                    user_id, movie_id, jwt_token=credentials.credentials
                )
                if interaction_data:
                    user_interactions_dict = {
                        "in_watchlist": interaction_data.get("in_watchlist", False),
                        "is_favorite": interaction_data.get(
                            "liked", False
                        ),  ***REMOVED*** 'liked' maps to 'is_favorite'
                        "user_rating": interaction_data.get("rating"),
                        "watch_progress": interaction_data.get("watch_progress", 0),
                        "is_watched": interaction_data.get("watched", False),
                    }
                else:
                    ***REMOVED*** No interaction data exists
                    user_interactions_dict = {
                        "in_watchlist": False,
                        "is_favorite": False,
                        "user_rating": None,
                        "watch_progress": 0,
                        "is_watched": False,
                    }
            except BackendClientError:
                logger.warning(
                    f"Failed to get user interactions for user {user_id}, movie {movie_id}"
                )
                user_interactions_dict = {
                    "in_watchlist": False,
                    "is_favorite": False,
                    "user_rating": None,
                    "watch_progress": 0,
                    "is_watched": False,
                }

        ***REMOVED*** Convert the dictionary to UserInteractions model
        user_interactions = UserInteractions(**user_interactions_dict)

        return MovieScreenData(
            movie=movie,
            cast=cast,
            trailers=trailers,
            similar_movies=similar_movies,
            user_interactions=user_interactions,
        )

    except BackendClientError as e:
        logger.error(f"Backend error for movie {movie_id}: {e}")
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Movie not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")


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
    logger.info(f"🔍 Debugging token extraction for movies list")
    logger.info(f"📋 Credentials present: {bool(credentials)}")

    if credentials and credentials.credentials:
        logger.info(f"🔑 Token present: {bool(credentials.credentials)}")
        logger.info(f"🔑 Token preview: {credentials.credentials[:20]}...")

        ***REMOVED*** Temporarily enable debug logging for JWT extraction
        auth_logger = logging.getLogger("bff_api.utils.auth")
        original_level = auth_logger.level
        auth_logger.setLevel(logging.DEBUG)

        user_id = extract_user_id_from_token(credentials.credentials)

        ***REMOVED*** Restore original logging level
        auth_logger.setLevel(original_level)

        logger.info(f"👤 Extracted user_id: {user_id}")
    else:
        logger.info("❌ No credentials or token found - treating as anonymous user")

    try:
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

        ***REMOVED*** Get movies from backend (anonymous - no auth needed)
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
            logger.info(f"🔄 Fetching user interactions for {len(movies)} movies")
            for list_movie in movies:
                list_movie_id = list_movie.get("id")
                if list_movie_id:
                    try:
                        interaction_data = await backend.get_user_movie_interaction(
                            user_id, list_movie_id, jwt_token=credentials.credentials
                        )
                        if interaction_data:
                            ***REMOVED*** Map user interaction data directly to movie fields
                            ***REMOVED*** for frontend compatibility
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
                            f"Failed to get user interaction for movie {list_movie_id}: {e}"
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
            logger.info("No user authenticated - setting default interaction values")
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

        return MovieListData(
            total=total_count,
            page=current_page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            results=movies,
        )

    except BackendClientError as e:
        logger.error(f"Backend error for movies list: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
