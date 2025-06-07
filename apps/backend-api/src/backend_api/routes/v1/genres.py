"""
Genre-related API routes (v1).
"""

import logging
import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException

***REMOVED*** Import movie-storage operations
from movie_storage.db.operations import (
    get_genre_by_id,
    get_genre_by_name,
    get_genres,
)
from sqlmodel import Session

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import response schemas
from backend_api.schemas.genre_schema import GenreResponse, GenresListResponse


***REMOVED*** Define a GenreDetailResponse type for consistency
class GenreDetailResponse(GenreResponse):
    """Detailed genre information - same as GenreResponse for now."""

    pass


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("", response_model=GenresListResponse)
async def list_genres(db: Session = Depends(get_db)) -> GenresListResponse:
    """
    Get a list of all movie genres.

    Returns all available genres with their IDs and names.
    """
    try:
        logger.info("Getting all genres")
        genres = get_genres(db)

        ***REMOVED*** Convert SQLModel objects to Pydantic response models
        genre_responses = [GenreResponse.model_validate(genre) for genre in genres]

        return GenresListResponse(genres=genre_responses, total=len(genre_responses))
    except Exception as e:
        logger.error(f"Error fetching genres: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{genre_id}", response_model=GenreResponse)
async def get_genre_details(genre_id: int, db: Session = Depends(get_db)) -> GenreResponse:
    """
    Get detailed information for a specific genre by its ID.
    """
    try:
        genre = get_genre_by_id(db, genre_id)

        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return GenreResponse.model_validate(genre)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching genre {genre_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/name/{name}", response_model=GenreResponse)
async def get_genre_by_name_route(name: str, db: Session = Depends(get_db)) -> GenreResponse:
    """
    Get genre information by its name.
    """
    try:
        genre = get_genre_by_name(db, name)

        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return GenreResponse.model_validate(genre)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching genre by name '{name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
