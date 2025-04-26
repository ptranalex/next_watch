"""
API routes for movie resources.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import List, Optional, Tuple, Dict, Union, Any
import logging
import traceback
from datetime import date, datetime
from sqlalchemy.sql import text, func, select
from fastapi import Response

***REMOVED*** Import movie-storage models only
from movie_storage.models import Movie, MovieGenreLink

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import response schemas
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse

***REMOVED*** Import API-specific query operations
from backend_api.queries import (
    get_top_rated_movies,
    get_movie_genres,
    get_movies_with_filters,
    get_movie_details_by_id,
    get_movie_details_by_tmdb_id,
    search_movies_by_title,
    get_genre_by_name,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


def format_movie_for_response(
    movie: Any, genres: List[Dict[str, Any]]
) -> MovieResponse:
    """
    Format a movie database row into a MovieResponse model.

    Args:
        movie: Movie database row or dictionary with attributes
        genres: List of genre dictionaries from get_movie_genres

    Returns:
        MovieResponse object with formatted data
    """
    ***REMOVED*** Convert genres to the expected format
    genre_list = [
        {"id": genre["id"], "name": genre["name"], "tmdb_id": genre["tmdb_id"]}
        for genre in genres
    ]

    ***REMOVED*** Check if movie is a dictionary or an object
    if isinstance(movie, dict):
        ***REMOVED*** It's already a dictionary
        movie_dict = movie.copy()
    else:
        ***REMOVED*** Create a dictionary from the movie object's attributes
        movie_dict = {
            "id": movie.id,
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "overview": movie.overview,
            "release_date": movie.release_date,
            "poster_url": movie.poster_url,
            "backdrop_url": movie.backdrop_url,
            "vote_average": movie.vote_average,
            "imdb_rating": movie.imdb_rating,
            "imdb_id": movie.imdb_id,
            "created_at": movie.created_at,
            "updated_at": movie.updated_at,
        }

    ***REMOVED*** Add genres to the dictionary
    movie_dict["genres"] = genre_list

    ***REMOVED*** Create and return the response object
    return MovieResponse.model_validate(movie_dict)


@router.get("/", response_model=MoviesListResponse)
async def list_movies(
    skip: int = Query(0, ge=0, description="Number of movies to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title", description="Field to sort by (title, release_date, imdb_rating)"
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Get a list of movies with pagination and optional filtering.

    Returns movies with basic information and pagination metadata.
    Supports filtering by genre ID, actor TMDB ID, and sorting by different fields.
    """
    try:
        ***REMOVED*** Debug info
        logger.info(
            f"Getting movies with skip={skip}, limit={limit}, genre_id={genre_id}, actor_id={actor_id}"
        )

        ***REMOVED*** Determine sorting options
        sort_field = (
            sort_by
            if sort_by in ["title", "release_date", "imdb_rating", "vote_count"]
            else "title"
        )

        ***REMOVED*** Get movies from database with pagination and filters using our query function
        movies, total_count = get_movies_with_filters(
            db,
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_id=actor_id,
            sort_by=sort_field,
            sort_desc=sort_desc,
        )
        logger.info(f"Found {len(movies)} movies")
        logger.info(f"Total matching movies in database: {total_count}")

        ***REMOVED*** Empty response if no movies
        if not movies:
            return MoviesListResponse(
                movies=[],
                total=0,
                page=1,
                page_size=limit,
            )

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Get the movie's genres
            genres = get_movie_genres(db, movie.id)

            ***REMOVED*** Format movie for response
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        ***REMOVED*** Calculate page number
        page = (skip // limit) + 1 if limit > 0 else 1

        ***REMOVED*** Create the paginated response
        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movies: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/top", response_model=MoviesListResponse)
async def get_top_movies_route(
    year: Optional[int] = Query(None, description="Filter by release year"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    limit: int = Query(10, ge=1, le=50, description="Max number of movies to return"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Get top-rated movies by IMDB rating.

    If year is provided, returns top movies for that year, otherwise returns top movies
    for the current year.
    """
    try:
        ***REMOVED*** If year is not provided, use current year
        current_year = year or datetime.now().year

        logger.info(f"Getting top movies for year {current_year}, genre_id={genre_id}")

        ***REMOVED*** Get movies using our query function
        movies, total_count = get_top_rated_movies(
            db_session=db,
            year=current_year,
            genre_id=genre_id,
            limit=limit,
            page=page,
            all_time=False,
        )

        logger.info(f"Found {len(movies)} top movies for year {current_year}")

        ***REMOVED*** Empty response if no movies
        if not movies:
            return MoviesListResponse(
                movies=[],
                total=0,
                page=page,
                page_size=limit,
            )

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Get the movie's genres
            genres = get_movie_genres(db, movie.id)

            ***REMOVED*** Format movie for response
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        ***REMOVED*** Create the paginated response
        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching top movies: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/top/all-time", response_model=MoviesListResponse)
async def get_all_time_top_movies(
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    min_votes: int = Query(100, ge=0, description="Minimum number of votes required"),
    limit: int = Query(10, ge=1, le=50, description="Max number of movies to return"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Get all-time top-rated movies by IMDB rating.

    Returns top movies across all years, with the option to filter by genre
    and set a minimum votes threshold.
    """
    try:
        logger.info(
            f"Getting all-time top movies with min_votes={min_votes}, genre_id={genre_id}"
        )

        ***REMOVED*** Get movies using our query function
        movies, total_count = get_top_rated_movies(
            db_session=db,
            genre_id=genre_id,
            limit=limit,
            page=page,
            all_time=True,
            min_votes=min_votes,
        )

        logger.info(f"Found {len(movies)} all-time top movies")

        ***REMOVED*** Empty response if no movies
        if not movies:
            return MoviesListResponse(
                movies=[],
                total=0,
                page=page,
                page_size=limit,
            )

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Get the movie's genres
            genres = get_movie_genres(db, movie.id)

            ***REMOVED*** Format movie for response
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        ***REMOVED*** Create the paginated response
        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching all-time top movies: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_details(
    movie_id: int, db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its database ID.

    Includes all movie fields, genres, and other metadata.
    """
    try:
        ***REMOVED*** Use our query function instead of directly calling movie-storage
        movie = get_movie_details_by_id(db, movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Get the movie's genres
        genres = get_movie_genres(db, movie["id"])

        ***REMOVED*** Format movie for response
        return format_movie_for_response(movie, genres)
    except HTTPException:
        raise
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movie {movie_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tmdb/{tmdb_id}", response_model=MovieResponse)
async def get_movie_by_tmdb(
    tmdb_id: int, db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its TMDB ID.

    Useful for looking up movies by their external ID.
    """
    try:
        ***REMOVED*** Use our query function instead of directly calling movie-storage
        movie = get_movie_details_by_tmdb_id(db, tmdb_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Get the movie's genres
        genres = get_movie_genres(db, movie["id"])

        ***REMOVED*** Format movie for response
        return format_movie_for_response(movie, genres)
    except HTTPException:
        raise
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movie by TMDB ID {tmdb_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search", response_model=MoviesListResponse)
async def search_movies(
    query: str = Query(..., description="Movie title to search for"),
    skip: int = Query(0, ge=0, description="Number of movies to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    actor_id: Optional[int] = Query(None, description="Filter by actor TMDB ID"),
    sort_by: str = Query(
        "title", description="Field to sort by (title, release_date, imdb_rating)"
    ),
    sort_desc: bool = Query(False, description="Sort in descending order"),
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Search for movies by title with optional filtering.

    Returns movies matching the search query with pagination metadata.
    Supports additional filtering by genre ID, actor TMDB ID, and sorting by different fields.
    """
    try:
        ***REMOVED*** Debug info
        logger.info(
            f"Searching movies with query={query}, skip={skip}, limit={limit}, genre_id={genre_id}, actor_id={actor_id}"
        )

        ***REMOVED*** Search movies from database with pagination and filters
        movies, total_count = search_movies_by_title(
            db,
            title_search=query,
            skip=skip,
            limit=limit,
            genre_id=genre_id,
            actor_id=actor_id,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

        logger.info(f"Found {len(movies)} movies matching '{query}'")

        ***REMOVED*** Empty response if no movies
        if not movies:
            return MoviesListResponse(
                movies=[],
                total=0,
                page=1,
                page_size=limit,
            )

        ***REMOVED*** Convert database rows to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Get the movie's genres
            genres = get_movie_genres(db, movie.id)

            ***REMOVED*** Format movie for response
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        ***REMOVED*** Calculate page number
        page = (skip // limit) + 1 if limit > 0 else 1

        ***REMOVED*** Create the paginated response
        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error searching movies with query '{query}': {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
