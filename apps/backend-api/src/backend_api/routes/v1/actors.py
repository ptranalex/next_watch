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
from backend_api.core.metrics import get_backend_metrics


***REMOVED*** Actor schemas
class ActorResponse(BaseModel):
    id: int
    name: str
    profile_path: Optional[str] = None
    biography: Optional[str] = None
    tmdb_id: Optional[int] = None
    popularity: Optional[float] = None


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
    Get a list of actors with pagination, ordered by popularity.

    Returns actors extracted from the credits table, with deduplication by TMDB person ID
    and sorted by popularity in descending order.
    """
    ***REMOVED*** Record metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_actor_operation("list", "started")

    try:
        from sqlmodel import select, text

        ***REMOVED*** Calculate offset
        offset = (page - 1) * limit

        ***REMOVED*** Use a proper SQL query to get unique actors ordered by popularity
        ***REMOVED*** DISTINCT ON ensures we get only one record per tmdb_person_id (the highest popularity one)
        query = text(
            """
            SELECT DISTINCT ON (tmdb_person_id) 
                tmdb_person_id, 
                name, 
                popularity, 
                profile_path
            FROM credit 
            WHERE department = 'Acting' 
                AND tmdb_person_id IS NOT NULL
                AND name IS NOT NULL
            ORDER BY tmdb_person_id, popularity DESC NULLS LAST
        """
        )

        ***REMOVED*** Execute the query to get all unique actors first
        result = db.execute(query)
        all_actors = result.fetchall()

        ***REMOVED*** Sort all actors by popularity (descending) and apply pagination
        sorted_actors = sorted(all_actors, key=lambda x: x.popularity or 0, reverse=True)
        paginated_actors = sorted_actors[offset : offset + limit]

        ***REMOVED*** Create actor response objects
        actors = []
        for row in paginated_actors:
            actors.append(
                ActorResponse(
                    id=row.tmdb_person_id,
                    name=row.name,
                    profile_path=row.profile_path,
                    tmdb_id=row.tmdb_person_id,
                    popularity=row.popularity,
                )
            )

        ***REMOVED*** Total count is the number of unique actors
        total = len(all_actors)

        ***REMOVED*** Record successful actor list operation
        if metrics:
            metrics.record_actor_operation("list", "success")

        return ActorsListResponse(actors=actors, total=total)

    except Exception as e:
        ***REMOVED*** Record error metrics
        if metrics:
            metrics.record_actor_operation("list", "error")
        logger.error(f"Error fetching actors: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor_details(actor_id: int, db: Session = Depends(get_db)) -> ActorResponse:
    """
    Get detailed information for a specific actor.
    """
    ***REMOVED*** Record metrics
    metrics = get_backend_metrics()
    if metrics:
        metrics.record_actor_operation("detail", "started")

    try:
        ***REMOVED*** Get credits for this actor
        credits = get_credits_by_person_id(db, actor_id)

        ***REMOVED*** Check if any credits found
        if not credits:
            ***REMOVED*** Record not found error
            if metrics:
                metrics.record_actor_operation("detail", "not_found")
            raise HTTPException(status_code=404, detail=f"Actor with ID {actor_id} not found")

        ***REMOVED*** Use the first credit to get actor information
        ***REMOVED*** (since actor information is stored in each credit)
        first_credit = credits[0]

        ***REMOVED*** Find the credit with highest popularity for this actor
        best_credit = max(credits, key=lambda c: c.popularity or 0)

        ***REMOVED*** Record successful actor detail operation
        if metrics:
            metrics.record_actor_operation("detail", "success")

        ***REMOVED*** Return actor details
        return ActorResponse(
            id=actor_id,
            name=best_credit.name,
            profile_path=best_credit.profile_path,
            biography=None,  ***REMOVED*** Not stored in our credit model
            tmdb_id=best_credit.tmdb_person_id,
            popularity=best_credit.popularity,
        )
    except HTTPException:
        raise
    except Exception as e:
        ***REMOVED*** Record error metrics
        if metrics:
            metrics.record_actor_operation("detail", "error")
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
