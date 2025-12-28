"""Movie storage operations."""

from datetime import date, datetime
from typing import Any

from config.logging import get_logger
from sqlalchemy import func
from sqlmodel import Session, select

from backend_api.db.operations.credit import (
    create_credits_from_tmdb_data,
    delete_credits_for_movie,
)
from backend_api.models import Movie, MovieGenreLink

logger = get_logger(__name__)


def create_movie(
    session: Session, movie_data: dict[str, Any], genre_ids: list[int] | None = None
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


def get_movie_by_id(session: Session, movie_id: int) -> Movie | None:
    """Get a movie by its primary key ID.

    Args:
        session: Database session
        movie_id: Movie ID

    Returns:
        Movie instance or None if not found
    """
    return session.get(Movie, movie_id)


def get_movie_by_tmdb_id(session: Session, tmdb_id: int) -> Movie | None:
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


def get_movie_by_imdb_id(session: Session, imdb_id: str) -> Movie | None:
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
    title_search: str | None = None,
    genre_id: int | None = None,
    sort_by: str = "title",
    sort_desc: bool = False,
) -> list[Movie]:
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


def update_movie(
    session: Session,
    movie_id: int,
    movie_data: dict[str, Any],
    genre_ids: list[int] | None = None,
) -> Movie | None:
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

    logger.debug(f"Updating movie: {movie.title} (ID: {movie_id})")

    ***REMOVED*** Create a copy to avoid modifying the input
    movie_dict = movie_data.copy()

    ***REMOVED*** Extract genre information if present
    if "genres" in movie_dict:
        del movie_dict["genres"]

    ***REMOVED*** Ensure language is not None to prevent SQL errors
    if movie_dict.get("language") is None:
        ***REMOVED*** Use original_language as fallback, or default to 'en'
        movie_dict["language"] = movie_dict.get("original_language") or "en"

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
    logger.debug(f"Movie updated successfully: {movie.title}")
    return movie


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
    links = session.exec(select(MovieGenreLink).where(MovieGenreLink.movie_id == movie_id)).all()
    for link in links:
        session.delete(link)
    logger.debug(f"Deleted {len(links)} genre links")

    ***REMOVED*** Delete the movie
    session.delete(movie)
    session.commit()
    logger.info("Movie deleted successfully")

    return True


def create_movie_from_tmdb_details(session: Session, tmdb_details: dict[str, Any]) -> Movie:
    """Create or update a movie from TMDB movie details API response.

    This function processes a TMDB movie details API response and maps it
    to our internal Movie and Credit models, including handling nested data
    like credits and collection information.

    Args:
        session: Database session
        tmdb_details: TMDB movie details API response

    Returns:
        Movie instance
    """
    ***REMOVED*** Check if movie already exists
    tmdb_id = tmdb_details.get("id")
    if not tmdb_id:
        logger.error("TMDB details missing movie ID")
        raise ValueError("TMDB movie details missing required ID field")

    existing_movie = get_movie_by_tmdb_id(session, tmdb_id)

    ***REMOVED*** Extract basic movie data
    movie_data = {
        "tmdb_id": tmdb_id,
        "imdb_id": tmdb_details.get("imdb_id"),
        "title": tmdb_details.get("title", "Unknown Title"),
        "original_title": tmdb_details.get("original_title"),
        "overview": tmdb_details.get("overview"),
        "tagline": tmdb_details.get("tagline"),
        "status": tmdb_details.get("status"),
        "language": tmdb_details.get("language"),
        "original_language": tmdb_details.get("original_language"),
        "runtime": tmdb_details.get("runtime"),
        "popularity": tmdb_details.get("popularity"),
        "vote_average": tmdb_details.get("vote_average"),
        "vote_count": tmdb_details.get("vote_count"),
        "budget": tmdb_details.get("budget"),
        "revenue": tmdb_details.get("revenue"),
        "adult": tmdb_details.get("adult"),
        "video": tmdb_details.get("video"),
        "tmdb_rating": tmdb_details.get("vote_average"),
        "imdb_rating": tmdb_details.get("imdb_rating"),
        "metacritic_rating": tmdb_details.get("metascore"),
        "rotten_tomatoes_rating": None,  ***REMOVED*** Will be populated by OMDB enrichment
        "awards": None,  ***REMOVED*** Will be populated by OMDB enrichment
    }

    ***REMOVED*** Process release date
    if release_date_str := tmdb_details.get("release_date"):
        try:
            movie_data["release_date"] = date.fromisoformat(release_date_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid release date format: {release_date_str}")

    ***REMOVED*** Process collection info
    if collection := tmdb_details.get("belongs_to_collection"):
        movie_data["belongs_to_collection_id"] = collection.get("id")
        movie_data["belongs_to_collection_name"] = collection.get("name")

    ***REMOVED*** Process URLs
    if poster_path := tmdb_details.get("poster_path"):
        movie_data["poster_url"] = f"https://image.tmdb.org/t/p/w500{poster_path}"

    if backdrop_path := tmdb_details.get("backdrop_path"):
        movie_data["backdrop_url"] = f"https://image.tmdb.org/t/p/original{backdrop_path}"

    movie_data["homepage"] = tmdb_details.get("homepage")

    ***REMOVED*** Extract genre IDs and ensure they exist in the database
    genre_ids: list[int] | None = None
    if genres := tmdb_details.get("genres"):
        ***REMOVED*** Import here to avoid circular imports
        from backend_api.db.operations.genre import create_genre, get_genre_by_tmdb_id

        ***REMOVED*** Process each genre and ensure it exists in database
        valid_genre_ids: list[int] = []
        for genre_data in genres:
            tmdb_genre_id = genre_data.get("id")
            if not tmdb_genre_id:
                continue

            ***REMOVED*** Check if genre exists, create if not
            db_genre = get_genre_by_tmdb_id(session, tmdb_genre_id)
            if not db_genre:
                genre_name = genre_data.get("name", f"Genre {tmdb_genre_id}")
                logger.info(f"Creating missing genre: {genre_name} (TMDB ID: {tmdb_genre_id})")
                db_genre = create_genre(session, name=genre_name, tmdb_id=tmdb_genre_id)

            ***REMOVED*** Add the database genre ID to our list (ensure it's not None)
            if db_genre.id is not None:
                valid_genre_ids.append(db_genre.id)

        genre_ids = valid_genre_ids if valid_genre_ids else None

    ***REMOVED*** Create or update movie
    if existing_movie and existing_movie.id is not None:
        logger.debug(f"Updating existing movie: {movie_data['title']} (ID: {existing_movie.id})")
        movie = update_movie(session, existing_movie.id, movie_data, genre_ids)
    else:
        logger.info(f"Creating new movie: {movie_data['title']}")
        movie = create_movie(session, movie_data, genre_ids)

    ***REMOVED*** Ensure movie was created/updated successfully
    if not movie or movie.id is None:
        raise RuntimeError(f"Failed to create or update movie: {movie_data['title']}")

    ***REMOVED*** Process credits if present
    if tmdb_details.get("credits"):
        ***REMOVED*** Delete existing credits
        delete_credits_for_movie(session, movie.id)

        ***REMOVED*** Create new credits
        create_credits_from_tmdb_data(session, movie.id, tmdb_details["credits"])

    ***REMOVED*** Process trailers if present
    if videos := tmdb_details.get("videos", {}).get("results", []):
        ***REMOVED*** Import here to avoid circular imports
        from backend_api.db.operations.trailer import (
            create_trailer,
            delete_trailers_for_movie,
        )

        ***REMOVED*** Delete existing trailers
        delete_trailers_for_movie(session, movie.id)

        ***REMOVED*** Create new trailers
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                trailer_data = {
                    "movie_id": movie.id,
                    "youtube_key": video.get("key"),
                    "name": video.get("name"),
                    "is_official": video.get("official", False),
                    "url_link": f"https://www.youtube.com/watch?v={video.get('key')}",
                }
                create_trailer(session, trailer_data)
                logger.debug(f"Created trailer: {trailer_data['name']} for movie {movie.title}")

    ***REMOVED*** Refresh the movie to include relationships
    session.refresh(movie)
    return movie
