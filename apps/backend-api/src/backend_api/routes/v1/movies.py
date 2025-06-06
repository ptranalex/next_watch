"""
Movie-related API routes (v1).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

***REMOVED*** Import database session dependency
from ...db.database import get_db
from ...errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from ...queries.movie_query import MovieQuery
from ...schemas.cast_schema import (
    CastMemberResponse,
    MovieCastResponse,
)

***REMOVED*** Import response schemas
from ...schemas.movie_schema import MovieResponse, MoviesListResponse
from ...schemas.trailer_schema import TrailerResponse

***REMOVED*** Import service and query
from ...services.movie_service import MovieService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


***REMOVED*** Get dependencies
def get_movie_service() -> MovieService:
    """Get movie service."""
    return MovieService()


def get_movie_query() -> MovieQuery:
    """Get movie query."""
    return MovieQuery()


***REMOVED*** Helper function
def format_movie_for_response(movie: Any, genres: List[Dict[str, Any]]) -> MovieResponse:
    """
    Format a movie database row into a MovieResponse model.
    """
    ***REMOVED*** Convert genres to the expected format
    genre_list = [
        {"id": genre["id"], "name": genre["name"], "tmdb_id": genre["tmdb_id"]} for genre in genres
    ]

    ***REMOVED*** Convert movie to dictionary based on its type
    if isinstance(movie, dict):
        ***REMOVED*** It's already a dictionary
        movie_dict = movie.copy()
    elif isinstance(movie, tuple):
        ***REMOVED*** If it's a tuple from a raw SQL query, assume column ordering
        ***REMOVED*** This is a simplification - adjust column names as needed
        columns = [
            "id",
            "title",
            "overview",
            "release_date",
            "poster_url",
            "backdrop_url",
        ]
        movie_dict = {col: movie[i] for i, col in enumerate(columns) if i < len(movie)}
    else:
        ***REMOVED*** Convert SQLAlchemy Row or other object to dictionary
        try:
            movie_dict = dict(movie._mapping)
        except (AttributeError, TypeError):
            ***REMOVED*** Fallback to __dict__ for other objects
            movie_dict = {k: v for k, v in movie.__dict__.items() if not k.startswith("_")}

    ***REMOVED*** Add genres to the dictionary
    movie_dict["genres"] = genre_list

    ***REMOVED*** Create and return the response object
    return MovieResponse.model_validate(movie_dict)


def create_pagination_response(
    movie_responses: List[MovieResponse],
    total_count: int,
    page: int,
    per_page: int,
) -> MoviesListResponse:
    """Create a standardized pagination response."""
    import math

    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1

    return MoviesListResponse(
        total=total_count,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        results=movie_responses,
    )


@router.get("/bulk", response_model=MoviesListResponse)
async def get_movies_bulk(
    ids: str = Query(..., description="Comma-separated list of movie IDs"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Max number of movies to return per page"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get multiple movies by their IDs with pagination support.

    This endpoint is optimized for bulk fetching of movies when you have
    a list of specific movie IDs. Supports pagination for large lists.

    Args:
        ids: Comma-separated list of movie IDs (e.g., "1,2,3,4,5")
        page: Page number for pagination
        limit: Maximum number of movies per page (max 200)
        db: Database session
        movie_query: Movie query service

    Returns:
        Paginated list of movies matching the provided IDs

    Example:
        GET /movies/bulk?ids=1,2,3,4,5&page=1&limit=50
    """
    try:
        ***REMOVED*** Parse movie IDs from comma-separated string
        try:
            movie_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
        except ValueError:
            raise ValidationError("Invalid movie IDs provided. Must be comma-separated integers.")

        if not movie_ids:
            return create_pagination_response([], 0, page, limit)

        if len(movie_ids) > 1000:  ***REMOVED*** Reasonable limit to prevent abuse
            raise ValidationError("Too many movie IDs provided. Maximum 1000 IDs per request.")

        ***REMOVED*** Calculate pagination for the movie IDs list
        skip = (page - 1) * limit
        paginated_ids = movie_ids[skip : skip + limit]

        ***REMOVED*** Get movies from database
        movies = movie_query.get_movies_by_ids(db, paginated_ids)

        if not movies:
            return create_pagination_response([], 0, page, limit)

        ***REMOVED*** Convert to response format
        movie_responses = []
        for movie in movies:
            if isinstance(movie, dict):
                movie_id = movie["id"]
            elif isinstance(movie, tuple):
                movie_id = movie[0]
            else:
                movie_id = movie.id

            genres = movie_query.get_movie_genres(db, movie_id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        ***REMOVED*** Calculate pagination metadata based on original movie_ids list
        total_count = len(movie_ids)
        return create_pagination_response(movie_responses, total_count, page, limit)

    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("", response_model=MoviesListResponse)
async def list_movies(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title",
        description="Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
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
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get a list of movies with pagination and optional filtering.
    """
    try:
        ***REMOVED*** Calculate skip from page number
        skip = (page - 1) * limit

        ***REMOVED*** Get movies from database with pagination and filters
        movies, total_count = movie_query.get_movies_with_filters(
            db,
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_tmdb_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
        )

        if not movies:
            return create_pagination_response([], 0, page, limit)

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Try different ways to access the ID based on the object type
            if isinstance(movie, dict):
                movie_id = movie["id"]
            elif isinstance(movie, tuple):
                ***REMOVED*** Assume ID is the first element in the tuple
                movie_id = movie[0]
            else:
                ***REMOVED*** Assume it's an object with an id attribute
                movie_id = movie.id

            genres = movie_query.get_movie_genres(db, movie_id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return create_pagination_response(movie_responses, total_count, page, limit)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/top", response_model=MoviesListResponse)
async def get_top_movies(
    year: Optional[int] = Query(None, description="Filter by release year"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    limit: int = Query(10, ge=1, le=50, description="Max number of movies to return"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get top rated movies for a specific year (or the current year if not specified).
    """
    try:
        ***REMOVED*** Calculate skip from page number
        skip = (page - 1) * limit

        ***REMOVED*** Get top movies for the year
        movies, total_count = movie_query.get_top_rated_movies(
            db, limit=limit, skip=skip, year=year, genre_id=genre_id
        )

        if not movies:
            return create_pagination_response([], 0, page, limit)

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Try different ways to access the ID based on the object type
            if isinstance(movie, dict):
                movie_id = movie["id"]
            elif isinstance(movie, tuple):
                ***REMOVED*** Assume ID is the first element in the tuple
                movie_id = movie[0]
            else:
                ***REMOVED*** Assume it's an object with an id attribute
                movie_id = movie.id

            genres = movie_query.get_movie_genres(db, movie_id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return create_pagination_response(movie_responses, total_count, page, limit)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/search", response_model=MoviesListResponse)
async def search_movies(
    q: str = Query(..., description="Search query for movie titles"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title",
        description="Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
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
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Search movies by title with pagination and optional filtering.

    Performs case-insensitive partial matching on movie titles and supports
    all the same filtering options as the main movie listing endpoint.
    """
    try:
        ***REMOVED*** Calculate skip from page number
        skip = (page - 1) * limit

        ***REMOVED*** Search movies using the query service
        movies, total_count = movie_query.search_movies_by_title(
            db,
            title_search=q,
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_tmdb_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
            imdb_rating=imdb_rating,
            rotten_tomatoes_rating=rotten_tomatoes_rating,
            metacritic_rating=metacritic_rating,
            year=year,
            start_year=start_year,
            end_year=end_year,
        )

        if not movies:
            return create_pagination_response([], 0, page, limit)

        ***REMOVED*** Convert to response format
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Try different ways to access the ID based on the object type
            if isinstance(movie, dict):
                movie_id = movie["id"]
            elif isinstance(movie, tuple):
                ***REMOVED*** Assume ID is the first element in the tuple
                movie_id = movie[0]
            else:
                ***REMOVED*** Assume it's an object with an id attribute
                movie_id = movie.id

            genres = movie_query.get_movie_genres(db, movie_id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return create_pagination_response(movie_responses, total_count, page, limit)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_details(
    movie_id: int = Path(..., ge=1, description="Movie database ID"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its database ID.
    """
    try:
        movie = movie_query.get_movie_details(db, movie_id)
        genres = movie_query.get_movie_genres(db, movie["id"])
        return format_movie_for_response(movie, genres)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/{movie_id}/cast", response_model=MovieCastResponse)
async def get_movie_cast(
    movie_id: int = Path(..., ge=1, description="Movie database ID"),
    db: Session = Depends(get_db),
    movie_service: MovieService = Depends(get_movie_service),
) -> MovieCastResponse:
    """
    Get cast information for a specific movie.
    """
    try:
        cast_members = movie_service.get_movie_cast(db, movie_id)

        ***REMOVED*** Convert to response objects
        cast_responses = []
        for cast_member in cast_members:
            cast_responses.append(CastMemberResponse.model_validate(cast_member))

        return MovieCastResponse(cast=cast_responses, movie_id=movie_id)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/tmdb/{tmdb_id}", response_model=MovieResponse)
async def get_movie_by_tmdb(
    tmdb_id: int = Path(..., ge=1, description="Movie TMDB ID"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its TMDB ID.
    """
    try:
        movie = movie_query.get_movie_by_tmdb_id(db, tmdb_id)
        genres = movie_query.get_movie_genres(db, movie["id"])
        return format_movie_for_response(movie, genres)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/{movie_id}/trailers", response_model=List[TrailerResponse])
async def get_movie_trailers(
    movie_id: int = Path(..., ge=1, description="Movie database ID"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> List[TrailerResponse]:
    """
    Get trailers for a specific movie.
    """
    try:
        trailers = movie_query.get_movie_trailers(db, movie_id)
        return [TrailerResponse.model_validate(trailer) for trailer in trailers]
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)
