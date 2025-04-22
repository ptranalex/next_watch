"""Movie storage operations."""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date

from sqlmodel import Session, select, or_
from sqlalchemy.sql import text
from sqlalchemy import func

from movie_storage.config.logging import with_logging
from movie_storage.models import Movie, Genre, MovieGenreLink, Credit

logger = logging.getLogger(__name__)


@with_logging(log_level="INFO")
def create_movie(
    session: Session, movie_data: Dict[str, Any], genre_ids: Optional[List[int]] = None
) -> Movie:
    """Create a movie record and associate it with genres.

    Args:
        session: Database session
        movie_data: Movie data dictionary
        genre_ids: List of genre IDs to associate with the movie

    Returns:
        Created Movie instance
    """
    ***REMOVED*** Create a copy to avoid modifying the input
    movie_dict = movie_data.copy()

    ***REMOVED*** Extract genre information if present to prevent SQLModel errors
    if "genres" in movie_dict:
        del movie_dict["genres"]

    ***REMOVED*** Create movie instance
    movie = Movie(**movie_dict)
    session.add(movie)
    session.flush()  ***REMOVED*** Flush to get the generated ID

    logger.info(f"Created movie: {movie.title} (ID: {movie.id})")

    ***REMOVED*** Associate genres if provided
    if genre_ids:
        for genre_id in genre_ids:
            link = MovieGenreLink(movie_id=movie.id, genre_id=genre_id)
            session.add(link)
        logger.debug(f"Associated movie with {len(genre_ids)} genres")

    session.commit()
    session.refresh(movie)
    return movie


def get_movie_by_id(session: Session, movie_id: int) -> Optional[Movie]:
    """Get a movie by its primary key ID.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        Movie instance or None if not found
    """
    return session.get(Movie, movie_id)


def get_movie_by_tmdb_id(session: Session, tmdb_id: int) -> Optional[Movie]:
    """Get a movie by its TMDB ID.

    Args:
        session: Database session
        tmdb_id: TMDB ID

    Returns:
        Movie instance or None if not found
    """
    statement = select(Movie).where(Movie.tmdb_id == tmdb_id)
    result = session.exec(statement).first()
    return result


def get_movie_by_imdb_id(session: Session, imdb_id: str) -> Optional[Movie]:
    """Get a movie by its IMDB ID.

    Args:
        session: Database session
        imdb_id: IMDB ID

    Returns:
        Movie instance or None if not found
    """
    statement = select(Movie).where(Movie.imdb_id == imdb_id)
    result = session.exec(statement).first()
    return result


def get_movies(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    title_search: Optional[str] = None,
    genre_id: Optional[int] = None,
    sort_by: str = "title",
    sort_desc: bool = False,
) -> List[Movie]:
    """Get movies with optional filtering and sorting.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        title_search: Optional title search string
        genre_id: Optional genre ID to filter by
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order

    Returns:
        List of Movie instances
    """
    query = select(Movie)

    ***REMOVED*** Apply title search if provided
    if title_search:
        search_pattern = f"%{title_search}%"
        query = query.where(func.lower(Movie.title).like(func.lower(search_pattern)))

    ***REMOVED*** Apply genre filter if provided
    if genre_id:
        query = query.join(MovieGenreLink).where(MovieGenreLink.genre_id == genre_id)

    ***REMOVED*** Apply sorting
    if hasattr(Movie, sort_by):
        sort_field = getattr(Movie, sort_by)
        if sort_desc:
            sort_field = sort_field.desc()
        query = query.order_by(sort_field)

    ***REMOVED*** Apply pagination
    movies = session.exec(query.offset(skip).limit(limit)).all()
    return list(movies)


@with_logging(log_level="INFO")
def update_movie(
    session: Session,
    movie_id: int,
    movie_data: Dict[str, Any],
    genre_ids: Optional[List[int]] = None,
) -> Optional[Movie]:
    """Update a movie record.

    Args:
        session: Database session
        movie_id: ID of the movie to update
        movie_data: Updated movie data
        genre_ids: List of genre IDs to associate with the movie

    Returns:
        Updated Movie instance or None if not found
    """
    movie = get_movie_by_id(session, movie_id)

    if not movie:
        logger.warning(f"Attempted to update non-existent movie with ID {movie_id}")
        return None

    logger.info(f"Updating movie: {movie.title} (ID: {movie_id})")

    ***REMOVED*** Create a copy to avoid modifying the input
    movie_dict = movie_data.copy()

    ***REMOVED*** Extract genre information if present
    if "genres" in movie_dict:
        del movie_dict["genres"]

    ***REMOVED*** Update movie attributes
    for key, value in movie_dict.items():
        if hasattr(movie, key):
            setattr(movie, key, value)

    ***REMOVED*** Set updated_at timestamp
    movie.updated_at = datetime.utcnow()

    ***REMOVED*** Update genre associations if provided
    if genre_ids is not None:
        ***REMOVED*** Remove existing genre links
        links = session.exec(
            select(MovieGenreLink).where(MovieGenreLink.movie_id == movie_id)
        ).all()
        for link in links:
            session.delete(link)
        logger.debug(f"Removed {len(links)} existing genre associations")

        ***REMOVED*** Add new genre links
        for genre_id in genre_ids:
            link = MovieGenreLink(movie_id=movie_id, genre_id=genre_id)
            session.add(link)
        logger.debug(f"Added {len(genre_ids)} new genre associations")

    session.add(movie)
    session.commit()
    session.refresh(movie)
    logger.info(f"Movie updated successfully: {movie.title}")
    return movie


@with_logging(log_level="INFO")
def delete_movie(session: Session, movie_id: int) -> bool:
    """Delete a movie record.

    Args:
        session: Database session
        movie_id: ID of the movie to delete

    Returns:
        True if the movie was deleted, False if it wasn't found
    """
    movie = get_movie_by_id(session, movie_id)

    if not movie:
        logger.warning(f"Attempted to delete non-existent movie with ID {movie_id}")
        return False

    logger.info(f"Deleting movie: {movie.title} (ID: {movie_id})")

    ***REMOVED*** Delete genre links
    links = session.exec(
        select(MovieGenreLink).where(MovieGenreLink.movie_id == movie_id)
    ).all()
    for link in links:
        session.delete(link)
    logger.debug(f"Deleted {len(links)} genre links")

    ***REMOVED*** Delete the movie
    session.delete(movie)
    session.commit()
    logger.info(f"Movie deleted successfully")

    return True


@with_logging(log_level="INFO")
def create_movie_from_tmdb_details(
    session: Session, tmdb_details: Dict[str, Any]
) -> Movie:
    """Create or update a movie from TMDB movie details API response.

    This function handles the conversion of a TMDB movie details API response
    to our internal Movie and Credit models, including handling nested data
    like credits and collection information.

    Args:
        session: Database session
        tmdb_details: TMDB movie details API response

    Returns:
        Created or updated Movie instance
    """
    ***REMOVED*** Check if movie already exists
    existing_movie = None
    if tmdb_details.get("id"):
        existing_movie = get_movie_by_tmdb_id(session, tmdb_details["id"])

    ***REMOVED*** Extract collection data if present
    collection_id = None
    collection_name = None
    if tmdb_details.get("belongs_to_collection"):
        collection = tmdb_details["belongs_to_collection"]
        collection_id = collection.get("id")
        collection_name = collection.get("name")

    ***REMOVED*** Prepare release date
    release_date = None
    if tmdb_details.get("release_date"):
        try:
            release_date = date.fromisoformat(tmdb_details["release_date"])
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid release date format: {tmdb_details.get('release_date')}"
            )

    ***REMOVED*** Extract first origin country if available
    origin_country = None
    if tmdb_details.get("origin_country") and len(tmdb_details["origin_country"]) > 0:
        origin_country = tmdb_details["origin_country"][0]

    ***REMOVED*** Create movie data dictionary
    movie_data = {
        "tmdb_id": tmdb_details.get("id"),
        "imdb_id": tmdb_details.get("imdb_id"),
        "title": tmdb_details.get("title", "Unknown Title"),
        "original_title": tmdb_details.get("original_title"),
        "overview": tmdb_details.get("overview"),
        "tagline": tmdb_details.get("tagline"),
        "status": tmdb_details.get("status"),
        "language": tmdb_details.get("language"),
        "original_language": tmdb_details.get("original_language"),
        "origin_country": origin_country,
        "belongs_to_collection_id": collection_id,
        "belongs_to_collection_name": collection_name,
        "release_date": release_date,
        "runtime": tmdb_details.get("runtime"),
        "poster_url": tmdb_details.get("poster_path"),
        "backdrop_url": tmdb_details.get("backdrop_path"),
        "homepage": tmdb_details.get("homepage"),
        "popularity": tmdb_details.get("popularity"),
        "vote_average": tmdb_details.get("vote_average"),
        "vote_count": tmdb_details.get("vote_count"),
        "budget": tmdb_details.get("budget"),
        "revenue": tmdb_details.get("revenue"),
        "adult": tmdb_details.get("adult", False),
        "video": tmdb_details.get("video", False),
        ***REMOVED*** Legacy fields for compatibility
        "tmdb_rating": tmdb_details.get("vote_average"),
        "imdb_rating": None,  ***REMOVED*** TMDB doesn't provide IMDb rating
    }

    ***REMOVED*** Get or create genre IDs
    genre_ids = []
    if tmdb_details.get("genres"):
        for genre_data in tmdb_details["genres"]:
            genre_id = genre_data.get("id")
            genre_name = genre_data.get("name")

            if genre_id and genre_name:
                ***REMOVED*** Get or create genre
                from movie_storage.db.operations import genre as genre_ops

                db_genre = genre_ops.get_genre_by_tmdb_id(session, genre_id)
                if not db_genre:
                    db_genre = genre_ops.create_genre(
                        session, name=genre_name, tmdb_id=genre_id
                    )
                genre_ids.append(db_genre.id)

    ***REMOVED*** Create or update the movie
    if existing_movie:
        logger.info(
            f"Updating existing movie: {movie_data['title']} (TMDB ID: {movie_data['tmdb_id']})"
        )
        movie = update_movie(session, existing_movie.id, movie_data, genre_ids)
    else:
        logger.info(
            f"Creating new movie: {movie_data['title']} (TMDB ID: {movie_data['tmdb_id']})"
        )
        movie = create_movie(session, movie_data, genre_ids)

    ***REMOVED*** Process credits if present
    if tmdb_details.get("credits") and tmdb_details["credits"].get("cast"):
        ***REMOVED*** First, remove existing credits
        existing_credits = session.exec(
            select(Credit).where(Credit.movie_id == movie.id)
        ).all()

        for credit in existing_credits:
            session.delete(credit)

        logger.debug(f"Removed {len(existing_credits)} existing credits")

        ***REMOVED*** Add new credits
        cast_data = tmdb_details["credits"]["cast"]
        for cast_member in cast_data:
            if not cast_member.get("id"):
                continue

            credit = Credit(
                movie_id=movie.id,
                tmdb_person_id=cast_member.get("id"),
                name=cast_member.get("name", "Unknown"),
                original_name=cast_member.get("original_name"),
                character=cast_member.get("character"),
                department=cast_member.get("known_for_department"),
                cast_id=cast_member.get("cast_id"),
                order=cast_member.get("order"),
                gender=cast_member.get("gender"),
                profile_path=cast_member.get("profile_path"),
                popularity=cast_member.get("popularity"),
                credit_id=cast_member.get("credit_id"),
                adult=cast_member.get("adult", False),
            )
            session.add(credit)

        session.commit()
        logger.info(f"Added {len(cast_data)} credits to movie")

    ***REMOVED*** Refresh the movie to include relationships
    session.refresh(movie)
    return movie
