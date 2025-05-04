"""
Movie-related API routes (v1).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import List, Optional, Dict, Any
import logging
import traceback
from datetime import datetime

***REMOVED*** Import movie-storage operations
from movie_storage.db.operations import (
    get_movie_by_id,
    get_credits_by_movie_id,
)

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import response schemas
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse
from backend_api.schemas.trailer_schema import TrailerResponse
from backend_api.schemas.cast_schema import (
    CastMemberResponse,
    MovieCastResponse,
)

***REMOVED*** Import API-specific query operations
from backend_api.queries import (
    get_top_rated_movies,
    get_movie_genres,
    get_movies_with_filters,
    get_movie_details_by_id,
    get_movie_details_by_tmdb_id,
    get_trailers_for_movie,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


***REMOVED*** Helper function from existing movies.py
def format_movie_for_response(
    movie: Any, genres: List[Dict[str, Any]]
) -> MovieResponse:
    """
    Format a movie database row into a MovieResponse model.
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
        ***REMOVED*** Convert SQLAlchemy Row to dictionary
        movie_dict = dict(movie._mapping)

    ***REMOVED*** Add genres to the dictionary
    movie_dict["genres"] = genre_list

    ***REMOVED*** Create and return the response object
    return MovieResponse.model_validate(movie_dict)


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
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Get a list of movies with pagination and optional filtering.
    """
    try:
        ***REMOVED*** Calculate skip from page number
        skip = (page - 1) * limit

        ***REMOVED*** Get movies from database with pagination and filters
        movies, total_count = get_movies_with_filters(
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
        )

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
            genres = get_movie_genres(db, movie.id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching movies: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_details(
    movie_id: int, db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its database ID.
    """
    try:
        movie = get_movie_details_by_id(db, movie_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        genres = get_movie_genres(db, movie["id"])
        return format_movie_for_response(movie, genres)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie {movie_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{movie_id}/cast", response_model=MovieCastResponse)
async def get_movie_cast(movie_id: int, db: Session = Depends(get_db)):
    """
    Get cast information for a specific movie.
    """
    try:
        ***REMOVED*** First verify the movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Get all credits for the movie
        credits = get_credits_by_movie_id(db, movie_id)

        ***REMOVED*** Filter for cast members only
        cast_members = []

        for credit in credits:
            ***REMOVED*** Filter for cast members (actors)
            if credit.department == "Acting" or credit.cast_id is not None:
                cast_member = {
                    "id": credit.id,
                    "actor_id": credit.tmdb_person_id,
                    "name": credit.name,
                    "character": credit.character,
                    "profile_path": credit.profile_path,
                    "order": credit.order,
                }
                cast_members.append(CastMemberResponse.model_validate(cast_member))

        ***REMOVED*** Sort cast by order if available
        cast_members.sort(key=lambda x: x.order if x.order is not None else 999)

        return MovieCastResponse(cast=cast_members, movie_id=movie_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cast for movie {movie_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/top", response_model=MoviesListResponse)
async def get_top_movies(
    year: Optional[int] = Query(None, description="Filter by release year"),
    genre_id: Optional[int] = Query(None, description="Filter by genre ID"),
    limit: int = Query(10, ge=1, le=50, description="Max number of movies to return"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    db: Session = Depends(get_db),
) -> MoviesListResponse:
    """
    Get top-rated movies by IMDB rating.
    """
    try:
        ***REMOVED*** If year is not provided, use current year
        current_year = year or datetime.now().year

        ***REMOVED*** Get movies using our query function
        movies, total_count = get_top_rated_movies(
            db_session=db,
            year=current_year,
            genre_id=genre_id,
            limit=limit,
            page=page,
            all_time=False,
        )

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
            genres = get_movie_genres(db, movie.id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching top movies: {str(e)}")
        logger.error(traceback.format_exc())
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
    """
    try:
        ***REMOVED*** Get movies using our query function
        movies, total_count = get_top_rated_movies(
            db_session=db,
            genre_id=genre_id,
            limit=limit,
            page=page,
            all_time=True,
            min_votes=min_votes,
        )

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
            genres = get_movie_genres(db, movie.id)
            movie_response = format_movie_for_response(movie, genres)
            movie_responses.append(movie_response)

        return MoviesListResponse(
            movies=movie_responses,
            total=total_count,
            page=page,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching all-time top movies: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/tmdb/{tmdb_id}", response_model=MovieResponse)
async def get_movie_by_tmdb(
    tmdb_id: int, db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Get detailed information for a specific movie by its TMDB ID.
    """
    try:
        movie = get_movie_details_by_tmdb_id(db, tmdb_id)

        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        genres = get_movie_genres(db, movie["id"])
        return format_movie_for_response(movie, genres)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie by TMDB ID {tmdb_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{movie_id}/trailers", response_model=List[TrailerResponse])
async def get_movie_trailers(
    movie_id: int, db: Session = Depends(get_db)
) -> List[TrailerResponse]:
    """
    Get all trailers for a movie.
    """
    try:
        ***REMOVED*** First check if movie exists
        movie = get_movie_details_by_id(db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Get trailers using our query function
        trailers = get_trailers_for_movie(db, movie_id)
        return [TrailerResponse.from_orm(t) for t in trailers]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trailers for movie {movie_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
