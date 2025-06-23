"""
Actor-related API routes (v1).
"""

import traceback
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query

***REMOVED*** Import fast-core dependencies and utilities
from fast_core.dependencies import get_pagination, get_request_id
from fast_core.responses import ResponseBuilder

***REMOVED*** Import schemas
from pydantic import BaseModel
from sqlmodel import Session

***REMOVED*** Import database session dependency
from backend_api.db.database import get_db

***REMOVED*** Import movie-storage operations
from backend_api.db.operations import (
    get_credits_by_person_id,
    get_movie_by_id,
)

***REMOVED*** Import models
from backend_api.models import Credit
from backend_api.schemas.movie_schema import MovieResponse, MoviesListResponse

from config.logging import get_logger


***REMOVED*** Actor schemas
class ActorResponse(BaseModel):
    id: int
    name: str
    profile_path: Optional[str] = None
    biography: Optional[str] = None
    tmdb_id: Optional[int] = None


class ActorDetailResponse(ActorResponse):
    """Detailed actor information including biography."""

    pass


class ActorsListResponse(BaseModel):
    actors: List[ActorResponse]
    total: int


class PaginatedActorResponse(BaseModel):
    """Paginated list of actors."""

    actors: List[ActorResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


logger = get_logger(__name__)

router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("", response_model=ActorsListResponse)
async def list_actors(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max number of actors to return"),
    db: Session = Depends(get_db),
) -> ActorsListResponse:
    """
    Get a list of actors with pagination.

    Returns actors extracted from the credits table, with deduplication by TMDB person ID.
    """
    try:
        ***REMOVED*** Get credits with department filter to get actors
        from backend_api.db.operations import get_credits

        ***REMOVED*** Calculate offset
        offset = (page - 1) * limit

        ***REMOVED*** Get credits for actors (Acting department) with pagination
        credits = get_credits(
            db, skip=offset, limit=limit * 3, department="Acting"
        )  ***REMOVED*** Get more to dedupe

        ***REMOVED*** Deduplicate by tmdb_person_id and create actor responses
        seen_actors = set()
        actors = []

        for credit in credits:
            if credit.tmdb_person_id and credit.tmdb_person_id not in seen_actors:
                seen_actors.add(credit.tmdb_person_id)
                actors.append(
                    ActorResponse(
                        id=credit.tmdb_person_id,
                        name=credit.name,
                        profile_path=credit.profile_path,
                        tmdb_id=credit.tmdb_person_id,
                    )
                )

                ***REMOVED*** Stop when we have enough unique actors
                if len(actors) >= limit:
                    break

        ***REMOVED*** For total count, get a rough estimate from distinct actors in acting credits
        ***REMOVED*** Note: This is an approximation as we'd need a more complex query for exact count
        total = len(seen_actors) + offset  ***REMOVED*** Rough estimate

        return ActorsListResponse(actors=actors, total=total)

    except Exception as e:
        logger.error(f"Error fetching actors: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor_details(actor_id: int, db: Session = Depends(get_db)) -> ActorResponse:
    """
    Get detailed information for a specific actor.
    """
    try:
        ***REMOVED*** Get credits for this actor
        credits = get_credits_by_person_id(db, actor_id)

        ***REMOVED*** Check if any credits found
        if not credits:
            raise HTTPException(status_code=404, detail=f"Actor with ID {actor_id} not found")

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
) -> MoviesListResponse:
    """
    Get movies featuring a specific actor.
    """
    try:
        ***REMOVED*** Get credits for this actor
        credits = get_credits_by_person_id(db, actor_id)

        ***REMOVED*** Check if actor exists
        if not credits:
            raise HTTPException(status_code=404, detail=f"Actor with ID {actor_id} not found")

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
                ***REMOVED*** Extract movie data safely regardless of type
                is_dict_like = (
                    hasattr(movie, "keys")
                    and hasattr(movie, "values")
                    and hasattr(movie, "__getitem__")
                )

                if is_dict_like:
                    movie_data = cast(Dict[str, Any], movie)
                elif hasattr(movie, "model_dump"):
                    movie_data = movie.model_dump()
                else:
                    ***REMOVED*** Fallback for other object types
                    movie_data = {
                        "id": getattr(movie, "id", movie_id),
                        "title": getattr(movie, "title", "Unknown"),
                        "tmdb_id": getattr(movie, "tmdb_id", None),
                    }

                ***REMOVED*** Create the response object
                movies.append(MovieResponse(**movie_data))

        ***REMOVED*** Return the paginated movie list
        import math

        total_count = len(movie_ids)
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        return MoviesListResponse(
            total=total_count,
            page=page,
            per_page=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            results=movies,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movies for actor {actor_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
