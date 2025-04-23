"""
API routes for movie resources.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import List, Optional
import logging
import traceback

***REMOVED*** Import movie-storage operations
from movie_storage.db.operations import (
    get_movies,
    get_movie_by_id,
    get_movie_by_tmdb_id,
)

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import response schemas
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=MoviesListResponse)
async def list_movies(
    skip: int = Query(0, ge=0, description="Number of movies to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    db: Session = Depends(get_db),
):
    """
    Get a list of movies with pagination.

    Returns movies with basic information and pagination metadata.
    """
    try:
        ***REMOVED*** Debug info
        logger.info(f"Getting movies with skip={skip}, limit={limit}")
        logger.info(f"DB object type: {type(db)}")

        ***REMOVED*** Get movies from database with pagination
        movies = get_movies(db, skip=skip, limit=limit)
        logger.info(f"Found {len(movies)} movies")

        ***REMOVED*** Empty response if no movies
        if not movies:
            return MoviesListResponse(
                movies=[],
                total=0,
                page=1,
                page_size=limit,
            )

        ***REMOVED*** Get total count (in production, use a dedicated count query)
        all_movies = get_movies(db)
        total_count = len(all_movies)
        logger.info(f"Total movies in database: {total_count}")

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        movie_responses = []
        for movie in movies:
            ***REMOVED*** Debug genre info
            logger.info(f"Movie {movie.id} has {len(movie.genres)} genres")

            ***REMOVED*** Convert genres to the expected format
            genre_list = [
                {"id": genre.id, "name": genre.name, "tmdb_id": genre.tmdb_id}
                for genre in movie.genres
            ]

            ***REMOVED*** Create a copy of the movie object for manipulation
            movie_dict = {
                "id": movie.id,
                "tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "overview": movie.overview,
                "release_date": movie.release_date,
                "poster_url": movie.poster_url,
                "backdrop_url": movie.backdrop_url,
                "vote_average": movie.vote_average,
                "imdb_id": movie.imdb_id,
                "genres": genre_list,
                "created_at": movie.created_at,
                "updated_at": movie.updated_at,
            }

            ***REMOVED*** Create the response object
            movie_responses.append(MovieResponse.model_validate(movie_dict))

        ***REMOVED*** Create the paginated response
        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=limit,
        )
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movies: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_details(movie_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific movie by its database ID.

    Includes all movie fields, genres, and other metadata.
    """
    try:
        movie = get_movie_by_id(db, movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Convert genres to the expected format
        genre_list = [
            {"id": genre.id, "name": genre.name, "tmdb_id": genre.tmdb_id}
            for genre in movie.genres
        ]

        ***REMOVED*** Create a copy of the movie object for manipulation
        movie_dict = {
            "id": movie.id,
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "overview": movie.overview,
            "release_date": movie.release_date,
            "poster_url": movie.poster_url,
            "backdrop_url": movie.backdrop_url,
            "vote_average": movie.vote_average,
            "imdb_id": movie.imdb_id,
            "genres": genre_list,
            "created_at": movie.created_at,
            "updated_at": movie.updated_at,
        }

        return MovieResponse.model_validate(movie_dict)
    except HTTPException:
        raise
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movie {movie_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tmdb/{tmdb_id}", response_model=MovieResponse)
async def get_movie_by_tmdb(tmdb_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific movie by its TMDB ID.

    Useful for looking up movies by their external ID.
    """
    try:
        movie = get_movie_by_tmdb_id(db, tmdb_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Convert genres to the expected format
        genre_list = [
            {"id": genre.id, "name": genre.name, "tmdb_id": genre.tmdb_id}
            for genre in movie.genres
        ]

        ***REMOVED*** Create a copy of the movie object for manipulation
        movie_dict = {
            "id": movie.id,
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "overview": movie.overview,
            "release_date": movie.release_date,
            "poster_url": movie.poster_url,
            "backdrop_url": movie.backdrop_url,
            "vote_average": movie.vote_average,
            "imdb_id": movie.imdb_id,
            "genres": genre_list,
            "created_at": movie.created_at,
            "updated_at": movie.updated_at,
        }

        return MovieResponse.model_validate(movie_dict)
    except HTTPException:
        raise
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching movie by TMDB ID {tmdb_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
