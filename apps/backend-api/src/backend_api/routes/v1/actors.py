"""
Actor-related API routes (v1).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session
from typing import List, Optional
import logging
import traceback

***REMOVED*** Import movie-storage operations
from movie_storage.db.operations import (
    get_credits_by_person_id,
    get_movie_by_id,
)

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import models
from movie_storage.models import Credit

***REMOVED*** Import schemas
from pydantic import BaseModel
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse


***REMOVED*** Actor schemas
class ActorResponse(BaseModel):
    id: int
    name: str
    profile_path: Optional[str] = None
    biography: Optional[str] = None
    tmdb_id: Optional[int] = None


class ActorsListResponse(BaseModel):
    actors: List[ActorResponse]
    total: int


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("", response_model=ActorsListResponse)
async def list_actors(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of actors to return"),
    db: Session = Depends(get_db),
):
    """
    Get a list of actors with pagination.
    """
    try:
        ***REMOVED*** This is a placeholder - implement actual actor listing functionality
        ***REMOVED*** For now, return empty response
        return ActorsListResponse(actors=[], total=0)
    except Exception as e:
        logger.error(f"Error fetching actors: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor_details(actor_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific actor.
    """
    try:
        ***REMOVED*** Get credits for this actor
        credits = get_credits_by_person_id(db, actor_id)

        ***REMOVED*** Check if any credits found
        if not credits:
            raise HTTPException(
                status_code=404, detail=f"Actor with ID {actor_id} not found"
            )

        ***REMOVED*** Use the first credit to get actor information
        ***REMOVED*** (since actor information is stored in each credit)
        first_credit = credits[0]

        ***REMOVED*** Return actor details
        return ActorResponse(
            id=actor_id,
            name=first_credit.name,
            profile_path=first_credit.profile_path,
            biography=None,  ***REMOVED*** Not stored in our credit model
            tmdb_id=first_credit.tmdb_person_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching actor {actor_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{actor_id}/movies", response_model=MoviesListResponse)
async def get_actor_movies(
    actor_id: int,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of movies to return"),
    db: Session = Depends(get_db),
):
    """
    Get movies featuring a specific actor.
    """
    try:
        ***REMOVED*** Get credits for this actor
        credits = get_credits_by_person_id(db, actor_id)

        ***REMOVED*** Check if actor exists
        if not credits:
            raise HTTPException(
                status_code=404, detail=f"Actor with ID {actor_id} not found"
            )

        ***REMOVED*** Get the movie IDs for this actor
        movie_ids = set(credit.movie_id for credit in credits if credit.movie_id)

        ***REMOVED*** Calculate pagination
        offset = (page - 1) * limit
        page_movie_ids = list(movie_ids)[offset : offset + limit]

        ***REMOVED*** Get the movie details for each ID
        movies = []
        for movie_id in page_movie_ids:
            movie = get_movie_by_id(db, movie_id)
            if movie:
                ***REMOVED*** If it's already a dictionary, use it directly
                if isinstance(movie, dict):
                    movies.append(MovieResponse(**movie))
                ***REMOVED*** Otherwise convert to a dict using SQLModel's methods
                elif hasattr(movie, "model_dump"):
                    movie_dict = movie.model_dump()
                    movies.append(MovieResponse(**movie_dict))
                else:
                    ***REMOVED*** Fallback for other cases
                    movie_dict = {
                        "id": movie.id,
                        "title": movie.title,
                        "tmdb_id": movie.tmdb_id,
                    }
                    movies.append(MovieResponse(**movie_dict))

        ***REMOVED*** Return the paginated movie list
        return MoviesListResponse(
            movies=movies, total=len(movie_ids), page=page, page_size=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movies for actor {actor_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
