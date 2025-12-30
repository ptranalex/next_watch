"""
Movie-related API routes (v1) with Fast Core integration.
"""

from typing import Any, cast

from config.logging import get_logger
from fast_core.dependencies import get_pagination, get_request_id
from fast_core.dependencies.common import PaginationParams
from fast_core.responses import PaginatedResponse, ResponseBuilder
from fastapi import APIRouter, Depends, Path, Query, Request
from sqlmodel import Session

from backend_api.core.metrics import (
    get_backend_metrics,
    track_bulk_operation,
    track_movie_operation,
    track_search_operation,
)

# Redis cache removed for bulk endpoints - too dynamic for effective caching
from backend_api.db.database import get_db
from backend_api.errors import (
    ResourceNotFoundError,
    ValidationError,
    service_error_to_http_exception,
)
from backend_api.queries.movie_query import MovieQuery
from backend_api.schemas.cast_schema import (
    CastMemberResponse,
    MovieCastResponse,
)

# Import response schemas
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse
from backend_api.schemas.trailer_schema import TrailerResponse

# Import service and query
from backend_api.services.movie_service import MovieService

logger = get_logger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])

# Initialize fast-core response builder
response_builder = ResponseBuilder(
    {
        "pagination": {
            "default_limit": 20,
            "max_limit": 100,
            "include_total_pages": True,
            "include_has_next_prev": True,
        },
        "detail": {
            "include_timestamps": True,
            "include_metadata": True,
        },
    }
)


def convert_paginated_response_to_movies_list(
    paginated_response: PaginatedResponse, request_id: str | None = None
) -> MoviesListResponse:
    """Convert fast-core paginated response to MoviesListResponse format.

    This helper maintains backward compatibility while using fast-core internally.
    """
    # fast-core models these as TypedDict with optional keys; in practice, our
    # ResponseBuilder always includes them. Use defensive .get() + sensible defaults
    # to satisfy typecheckers and avoid runtime KeyErrors.
    pagination = paginated_response.get("pagination") or {}
    results = cast(list[Any], paginated_response.get("results") or [])

    page = pagination.get("page", 1)
    per_page = pagination.get("per_page", len(results) or 1) or 1
    total = pagination.get("total", len(results))
    total_pages = pagination.get("total_pages")
    if total_pages is None:
        total_pages = (total + per_page - 1) // per_page if per_page else 1
    has_next = pagination.get("has_next", page < total_pages)
    has_prev = pagination.get("has_prev", page > 1)

    return MoviesListResponse(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        results=results,
    )


# Get dependencies
def get_movie_service() -> MovieService:
    """Get movie service."""
    return MovieService()


def get_movie_query() -> MovieQuery:
    """Get movie query."""
    return MovieQuery()


# Helper function (enhanced with request tracking)
def format_movie_for_response(
    movie: Any, genres: list[dict[str, Any]], request_id: str | None = None
) -> MovieResponse:
    """
    Format a movie database row into a MovieResponse model with request tracking.
    """
    # Convert genres to the expected format
    genre_list = [
        {"id": genre["id"], "name": genre["name"], "tmdb_id": genre["tmdb_id"]} for genre in genres
    ]

    # Convert movie to dictionary based on its features
    is_dict_like = (
        hasattr(movie, "keys") and hasattr(movie, "values") and hasattr(movie, "__getitem__")
    )

    if is_dict_like:
        movie_dict = cast(dict[str, Any], movie)
    else:
        # Convert SQLAlchemy Row or other object to dictionary
        try:
            movie_dict = dict(movie._mapping)
        except (AttributeError, TypeError):
            # Fallback to __dict__ for other objects
            movie_dict = {k: v for k, v in movie.__dict__.items() if not k.startswith("_")}

    # Add genres to the dictionary
    movie_dict["genres"] = genre_list

    # Create and return the response object
    return MovieResponse.model_validate(movie_dict)


def create_pagination_response(
    movie_responses: list[MovieResponse],
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


# Helper function to safely get movie ID
def get_movie_id(movie: Any) -> int:
    """Extract the movie ID safely from any movie object type."""
    # Dictionary-like check
    if hasattr(movie, "keys") and hasattr(movie, "values") and hasattr(movie, "__getitem__"):
        try:
            movie_dict = cast(dict[str, Any], movie)
            return int(movie_dict.get("id", 0))
        except (KeyError, TypeError, ValueError):
            pass

    # Object with id attribute
    try:
        return int(getattr(movie, "id", 0))
    except (TypeError, ValueError):
        return 0


# Bulk endpoint caching removed - too dynamic for effective cache hit rates
# The materialized view provides the performance optimization instead


async def _get_bulk_movies_internal(
    ids: str, page: int, limit: int, db: Session, movie_query: MovieQuery
) -> MoviesListResponse:
    """Internal function for bulk movies logic (used by both cached and non-cached paths)."""
    # Parse movie IDs from comma-separated string
    try:
        movie_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
    except ValueError:
        raise ValidationError("Invalid movie IDs provided. Must be comma-separated integers.")

    if not movie_ids:
        return create_pagination_response([], 0, page, limit)

    if len(movie_ids) > 1000:  # Reasonable limit to prevent abuse
        raise ValidationError("Too many movie IDs provided. Maximum 1000 IDs per request.")

    # Record bulk operation metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_movie_operation("bulk", "success")
        metrics.record_bulk_operation(
            "bulk_get", len(movie_ids), 0.0
        )  # Duration will be tracked by decorator

    # Calculate pagination for the movie IDs list
    skip = (page - 1) * limit
    paginated_ids = movie_ids[skip : skip + limit]

    # Get movies from database using precomputed metadata (Netflix pattern)
    movies = movie_query.get_movies_by_ids(db, paginated_ids, use_precomputed=True)

    if not movies:
        return create_pagination_response([], 0, page, limit)

    # Convert to response format (movies already have genres from precomputed data)
    movie_responses = []
    for movie in movies:
        # Movies from precomputed data already have genres included
        movie_response = MovieResponse.model_validate(movie)
        movie_responses.append(movie_response)

    # Calculate pagination metadata based on original movie_ids list
    total_count = len(movie_ids)
    return create_pagination_response(movie_responses, total_count, page, limit)


@router.get("/bulk", response_model=MoviesListResponse)
@track_bulk_operation
async def get_movies_bulk(
    ids: str = Query(..., description="Comma-separated list of movie IDs"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Max number of movies to return per page"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get multiple movies by their IDs with high-performance precomputed metadata.

    This endpoint implements Netflix-style architecture patterns:
    - Precomputed metadata via materialized views for instant response
    - Bulk operations to avoid N+1 queries
    - Fallback to real-time aggregation when needed

    Args:
        ids: Comma-separated list of movie IDs (e.g., "1,2,3,4,5")
        page: Page number for pagination
        limit: Maximum number of movies per page (max 200)
        db: Database session
        movie_query: Movie query service

    Returns:
        Paginated list of movies with complete metadata

    Example:
        GET /movies/bulk?ids=1,2,3,4,5&page=1&limit=50
    """
    try:
        # Use materialized view for high performance (Netflix-style precomputed metadata)
        return await _get_bulk_movies_internal(ids, page, limit, db, movie_query)

    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("", response_model=MoviesListResponse)
async def list_movies(
    request: Request,
    pagination: PaginationParams = get_pagination(max_page_size=100),
    request_id: str = Depends(get_request_id),
    genre_id: int | None = Query(None, description="Filter by genre ID"),
    actor_id: int | None = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title",
        description="Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    imdb_rating: float | None = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: int | None = Query(None, description="Filter by release year"),
    start_year: int | None = Query(None, description="Filter by start year (inclusive)"),
    end_year: int | None = Query(None, description="Filter by end year (inclusive)"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get a list of movies with pagination and optional filtering (Fast Core enhanced).
    """
    # Record metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_movie_operation("list", "started")

    try:
        logger.debug(
            f"[{request_id}] Fetching movies - page: {pagination.page}, limit: {pagination.limit}, "
            f"genre_id: {genre_id}, actor_id: {actor_id}, sort_by: {sort_by}, sort_desc: {sort_desc}",
            extra={"request_id": request_id, "endpoint": "list_movies"},
        )

        # Get movies from database with pagination and filters using fast-core pagination
        movies, total_count = movie_query.get_movies_with_filters(
            db,
            skip=pagination.offset,
            limit=pagination.limit,
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
            logger.debug(f"[{request_id}] No movies found with given filters")
            paginated_response = response_builder.paginated(
                items=[],
                page=pagination.page,
                limit=pagination.limit,
                total=0,
                metadata={"request_id": request_id, "filters_applied": True},
            )
            return convert_paginated_response_to_movies_list(paginated_response, request_id)

        # Get all movie IDs for bulk genre fetching (eliminates N+1 queries)
        movie_ids_for_genres = [get_movie_id(movie) for movie in movies]
        genres_by_movie = movie_query.get_movie_genres_bulk(db, movie_ids_for_genres)

        # Convert to response format with request tracking
        movie_responses = []
        for movie in movies:
            # Get movie ID safely
            movie_id = get_movie_id(movie)
            genres = genres_by_movie.get(movie_id, [])  # Get genres from bulk result
            movie_response = format_movie_for_response(movie, genres, request_id)
            movie_responses.append(movie_response)

        logger.debug(
            f"[{request_id}] Successfully fetched {len(movie_responses)} movies",
            extra={
                "request_id": request_id,
                "count": len(movie_responses),
                "total": total_count,
            },
        )

        # Record successful movie list request
        if metrics:
            metrics.record_movie_operation("list", "success")

        # Use fast-core response builder for consistent pagination
        paginated_response = response_builder.paginated(
            items=movie_responses,
            page=pagination.page,
            limit=pagination.limit,
            total=total_count,
            metadata={
                "request_id": request_id,
                "filters_applied": {
                    "genre_id": genre_id,
                    "actor_id": actor_id,
                    "sort_by": sort_by,
                    "sort_desc": sort_desc,
                },
            },
        )
        return convert_paginated_response_to_movies_list(paginated_response, request_id)
    except (ResourceNotFoundError, ValidationError) as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_operation("list", "validation_error")
        logger.error(
            f"[{request_id}] Error fetching movies: {str(e)}",
            extra={"request_id": request_id},
        )
        raise service_error_to_http_exception(e)


@router.get("/top", response_model=MoviesListResponse)
async def get_top_movies(
    year: int | None = Query(None, description="Filter by release year"),
    genre_id: int | None = Query(None, description="Filter by genre ID"),
    limit: int = Query(10, ge=1, le=50, description="Max number of movies to return"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Get top rated movies for a specific year (or the current year if not specified).
    """
    try:
        # Calculate skip from page number
        skip = (page - 1) * limit

        # Get top movies for the year
        movies, total_count = movie_query.get_top_rated_movies(
            db, limit=limit, skip=skip, year=year, genre_id=genre_id
        )

        if not movies:
            return create_pagination_response([], 0, page, limit)

        # Get all movie IDs for bulk genre fetching (eliminates N+1 queries)
        movie_ids_for_genres = [get_movie_id(movie) for movie in movies]
        genres_by_movie = movie_query.get_movie_genres_bulk(db, movie_ids_for_genres)

        # Convert to response format
        movie_responses = []
        for movie in movies:
            # Get movie ID safely
            movie_id = get_movie_id(movie)
            genres = genres_by_movie.get(movie_id, [])  # Get genres from bulk result
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return create_pagination_response(movie_responses, total_count, page, limit)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/search", response_model=MoviesListResponse)
@track_search_operation
async def search_movies(
    q: str = Query(..., description="Search query for movie titles"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: int | None = Query(None, description="Filter by genre ID"),
    actor_id: int | None = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title",
        description="Field to sort by (title, release_date, imdb_rating, rotten_tomatoes_rating, metacritic_rating)",
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    imdb_rating: float | None = Query(
        None, ge=0, le=10, description="Filter by minimum IMDb rating"
    ),
    rotten_tomatoes_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Rotten Tomatoes rating"
    ),
    metacritic_rating: int | None = Query(
        None, ge=0, le=100, description="Filter by minimum Metacritic rating"
    ),
    year: int | None = Query(None, description="Filter by release year"),
    start_year: int | None = Query(None, description="Filter by start year (inclusive)"),
    end_year: int | None = Query(None, description="Filter by end year (inclusive)"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MoviesListResponse:
    """
    Search movies by title with pagination and optional filtering.

    Performs case-insensitive partial matching on movie titles and supports
    all the same filtering options as the main movie listing endpoint.
    """
    try:
        # Count applied filters for metrics
        filters_count = sum(
            [
                1
                for x in [
                    genre_id,
                    actor_id,
                    imdb_rating,
                    rotten_tomatoes_rating,
                    metacritic_rating,
                    year,
                    start_year,
                    end_year,
                ]
                if x is not None
            ]
        )

        # Record search operation metrics
        metrics = get_backend_metrics()
        if metrics:
            metrics.record_movie_operation("search", "success")
            # Duration will be tracked by decorator, pass 0.0 for now
            metrics.record_movie_search("title", filters_count, 0.0)

        # Calculate skip from page number
        skip = (page - 1) * limit

        # Search movies using the query service
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

        # Get all movie IDs for bulk genre fetching (eliminates N+1 queries)
        movie_ids_for_genres = [get_movie_id(movie) for movie in movies]
        genres_by_movie = movie_query.get_movie_genres_bulk(db, movie_ids_for_genres)

        # Convert to response format
        movie_responses = []
        for movie in movies:
            # Get movie ID safely
            movie_id = get_movie_id(movie)
            genres = genres_by_movie.get(movie_id, [])  # Get genres from bulk result
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return create_pagination_response(movie_responses, total_count, page, limit)
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)


@router.get("/{movie_id}", response_model=MovieResponse)
@track_movie_operation
async def get_movie_details(
    movie_id: int = Path(..., ge=1, description="Movie database ID"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its database ID.
    """
    # Record metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_movie_operation("detail", "started")

    try:
        movie = movie_query.get_movie_details(db, movie_id)
        genres = movie_query.get_movie_genres(db, movie["id"])

        # Record successful movie detail request
        if metrics:
            metrics.record_movie_operation("detail", "success")

        return format_movie_for_response(movie, genres)
    except (ResourceNotFoundError, ValidationError) as e:
        # Record error metrics
        if metrics:
            metrics.record_movie_operation(
                "detail",
                "not_found" if isinstance(e, ResourceNotFoundError) else "validation_error",
            )
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

        # Convert to response objects
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


@router.get("/{movie_id}/trailers", response_model=list[TrailerResponse])
async def get_movie_trailers(
    movie_id: int = Path(..., ge=1, description="Movie database ID"),
    db: Session = Depends(get_db),
    movie_query: MovieQuery = Depends(get_movie_query),
) -> list[TrailerResponse]:
    """
    Get trailers for a specific movie.
    """
    try:
        trailers = movie_query.get_movie_trailers(db, movie_id)
        return [TrailerResponse.model_validate(trailer) for trailer in trailers]
    except (ResourceNotFoundError, ValidationError) as e:
        raise service_error_to_http_exception(e)
