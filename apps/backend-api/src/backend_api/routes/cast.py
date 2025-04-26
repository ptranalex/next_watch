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
    MovieCastResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cast"])


@router.get("/movies/{movie_id}/cast", response_model=MovieCastResponse)
async def get_movie_cast(movie_id: int, db: Session = Depends(get_db)):
    """
    Get cast information for a specific movie.

    Returns only cast members (actors), excluding crew members.
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
        ***REMOVED*** Get detailed stack trace
        stack_trace = traceback.format_exc()
        logger.error(f"Error fetching cast for movie {movie_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
