"""Main BFF routes for screen-oriented endpoints."""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel

from bff_api.services.backend_client import BackendClient, BackendClientError

logger = logging.getLogger(__name__)
router = APIRouter()


class HomeScreenData(BaseModel):
    """Data model for home screen."""

    featured_movies: List[Dict[str, Any]]
    popular_movies: List[Dict[str, Any]]
    recent_releases: List[Dict[str, Any]]
    user_recommendations: List[Dict[str, Any]]
    genres: List[Dict[str, Any]]


class MovieScreenData(BaseModel):
    """Data model for movie detail screen."""

    movie: Dict[str, Any]
    cast: List[Dict[str, Any]]
    similar_movies: List[Dict[str, Any]]
    user_interactions: Dict[str, Any]


class MovieListData(BaseModel):
    """Data model for movie listing screen."""

    movies: List[Dict[str, Any]]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class GenreScreenData(BaseModel):
    """Data model for genre screen."""

    genre: Dict[str, Any]
    movies: List[Dict[str, Any]]
    total_count: int
    page: int
    has_next: bool


def get_backend_client() -> BackendClient:
    """Dependency to get backend client."""
    ***REMOVED*** This will be replaced by dependency injection in main.py
    from bff_api.config.app import settings

    return BackendClient(settings)


@router.get("/home", response_model=HomeScreenData)
async def get_home_screen(
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> HomeScreenData:
    """Get aggregated data for home screen.

    Args:
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Aggregated home screen data
    """
    try:
        ***REMOVED*** Fetch data concurrently (in real implementation, use asyncio.gather)
        featured_movies_response = await backend.get_movies(
            page=1, limit=10, featured=True, user_id=user_id
        )
        popular_movies_response = await backend.get_movies(
            page=1, limit=20, sort="popularity", user_id=user_id
        )
        recent_releases_response = await backend.get_movies(
            page=1, limit=15, sort="release_date", user_id=user_id
        )
        genres = await backend.get_genres()

        ***REMOVED*** Handle user recommendations
        user_recommendations = []
        if user_id:
            try:
                recommendations_response = await backend.get_movies(
                    page=1, limit=20, recommended_for=user_id, user_id=user_id
                )
                user_recommendations = recommendations_response.get("data", [])
            except BackendClientError:
                logger.warning(f"Failed to get recommendations for user {user_id}")

        return HomeScreenData(
            featured_movies=featured_movies_response.get("data", []),
            popular_movies=popular_movies_response.get("data", []),
            recent_releases=recent_releases_response.get("data", []),
            user_recommendations=user_recommendations,
            genres=genres,
        )

    except BackendClientError as e:
        logger.error(f"Backend error in home screen: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/movies/{movie_id}", response_model=MovieScreenData)
async def get_movie_screen(
    movie_id: int = Path(..., description="Movie ID"),
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieScreenData:
    """Get aggregated data for movie detail screen.

    Args:
        movie_id: Movie ID
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Aggregated movie detail screen data
    """
    try:
        ***REMOVED*** Get movie details
        movie = await backend.get_movie(movie_id, user_id=user_id)

        ***REMOVED*** Get additional data (implement these endpoints in backend)
        ***REMOVED*** cast = await backend.get_movie_cast(movie_id)
        ***REMOVED*** similar_movies = await backend.get_similar_movies(movie_id, user_id=user_id)

        ***REMOVED*** Placeholder for now
        cast: List[Dict[str, Any]] = []
        similar_movies: List[Dict[str, Any]] = []

        ***REMOVED*** User interactions (watchlist, favorite, rating)
        user_interactions = {}
        if user_id:
            ***REMOVED*** Implementation would check user's watchlist, favorites, ratings
            user_interactions = {
                "in_watchlist": False,
                "is_favorite": False,
                "user_rating": None,
                "watch_progress": 0,
            }

        return MovieScreenData(
            movie=movie,
            cast=cast,
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
    sort: Optional[str] = Query(
        None, description="Sort order (popularity, release_date, rating, title)"
    ),
    sort_desc: Optional[bool] = Query(True, description="Sort in descending order"),
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> MovieListData:
    """Get paginated list of movies with filters.

    Args:
        page: Page number for pagination
        limit: Number of items per page
        genre_id: Optional genre filter
        sort: Sort field (popularity, release_date, rating, title)
        sort_desc: Sort in descending order
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Paginated movie list with user interactions
    """
    try:
        ***REMOVED*** Build filter parameters
        filters: Dict[str, Any] = {}
        if genre_id is not None:
            filters["genre_id"] = genre_id
        if sort:
            filters["sort"] = sort
        if sort_desc is not None:
            filters["sort_desc"] = sort_desc

        ***REMOVED*** Get movies from backend
        movies_response = await backend.get_movies(
            page=page, limit=limit, user_id=user_id, **filters
        )

        movies = movies_response.get("data", [])
        total_count = movies_response.get("total", 0)
        has_next = movies_response.get("has_next", False)
        has_prev = page > 1

        return MovieListData(
            movies=movies,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=has_next,
            has_prev=has_prev,
        )

    except BackendClientError as e:
        logger.error(f"Backend error for movies list: {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/genres/{genre_id}", response_model=GenreScreenData)
async def get_genre_screen(
    genre_id: int = Path(..., description="Genre ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort order"),
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> GenreScreenData:
    """Get aggregated data for genre screen.

    Args:
        genre_id: Genre ID
        page: Page number for pagination
        limit: Number of items per page
        sort: Sort order
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Aggregated genre screen data
    """
    try:
        ***REMOVED*** Get genre details and movies
        movies_response = await backend.get_movies(
            page=page,
            limit=limit,
            genre_id=genre_id,
            sort=sort,
            user_id=user_id,
        )

        ***REMOVED*** Get genre info (implement this endpoint in backend)
        ***REMOVED*** For now, create basic genre info
        genre = {
            "id": genre_id,
            "name": "Genre Name",  ***REMOVED*** Would come from backend
            "description": "Genre description",
        }

        movies = movies_response.get("data", [])
        total_count = movies_response.get("total", 0)
        has_next = movies_response.get("has_next", False)

        return GenreScreenData(
            genre=genre,
            movies=movies,
            total_count=total_count,
            page=page,
            has_next=has_next,
        )

    except BackendClientError as e:
        logger.error(f"Backend error for genre {genre_id}: {e}")
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Genre not found")
        raise HTTPException(status_code=502, detail="Backend service unavailable")


@router.get("/search")
async def search_screen(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(
        None, description="User ID for personalized content"
    ),
    backend: BackendClient = Depends(get_backend_client),
) -> Dict[str, Any]:
    """Get search results for search screen.

    Args:
        q: Search query
        page: Page number for pagination
        limit: Number of items per page
        user_id: Optional user ID for personalized content
        backend: Backend client dependency

    Returns:
        Search results with pagination
    """
    try:
        results = await backend.search_movies(
            query=q,
            page=page,
            limit=limit,
            user_id=user_id,
        )

        return {
            "query": q,
            "results": results.get("data", []),
            "total_count": results.get("total", 0),
            "page": page,
            "has_next": results.get("has_next", False),
        }

    except BackendClientError as e:
        logger.error(f"Backend error for search '{q}': {e}")
        raise HTTPException(status_code=502, detail="Backend service unavailable")
