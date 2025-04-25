"""
API routes for cast and crew resources.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from typing import List, Optional
import logging
import traceback

***REMOVED*** Import movie-storage operations
from movie_storage.db.operations import (
    get_credits_by_movie_id,
    get_movie_by_id,
)

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import response schemas
from backend_api.schemas.cast_schema import (
    CastMemberResponse,
    CrewMemberResponse,
    MovieCreditsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cast"])


@router.get("/movies/{movie_id}/cast", response_model=MovieCreditsResponse)
async def get_movie_cast(movie_id: int, db: Session = Depends(get_db)):
    """
    Get cast and crew information for a specific movie.

    Returns cast members (actors) and crew members (directors, writers, etc.)
    separated into their respective categories.
    """
    try:
        ***REMOVED*** First verify the movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        ***REMOVED*** Get all credits for the movie
        credits = get_credits_by_movie_id(db, movie_id)

        ***REMOVED*** Separate cast and crew
        cast_members = []
        crew_members = []

        for credit in credits:
            ***REMOVED*** Filter for cast members (actors)
            if credit.department == "Acting" or credit.cast_id is not None:
                cast_member = {
                    "id": credit.id,
                    "tmdb_person_id": credit.tmdb_person_id,
                    "name": credit.name,
                    "character": credit.character,
                    "profile_path": credit.profile_path,
                    "order": credit.order,
                }
                cast_members.append(CastMemberResponse.model_validate(cast_member))
            ***REMOVED*** Filter for crew members
            elif credit.department and credit.job:
                crew_member = {
                    "id": credit.id,
                    "tmdb_person_id": credit.tmdb_person_id,
                    "name": credit.name,
                    "department": credit.department,
                    "job": credit.job,
                    "profile_path": credit.profile_path,
                }
                crew_members.append(CrewMemberResponse.model_validate(crew_member))

        ***REMOVED*** Sort cast by order if available
        cast_members.sort(key=lambda x: x.order if x.order is not None else 999)

        return MovieCreditsResponse(
            cast=cast_members, crew=crew_members, movie_id=movie_id
        )

    except HTTPException:
        raise
    except Exception as e:
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching cast for movie {movie_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
