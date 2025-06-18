"""
from config.logging import get_logger
User movie interaction service module.

This service handles business logic related to how users interact with movies,
including tracking movies as watched, liked, and in watchlists.
"""

import csv
import io
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from dateutil import parser as date_parser
from sqlalchemy import func
from sqlmodel import Session, select

from config.logging import get_logger
from backend_api.db.operations import (
    delete_user_movie_interaction,
    get_movie_by_id,
    get_user_movie_interaction,
    toggle_user_movie_interaction_flag,
)
from backend_api.errors import ResourceNotFoundError, ValidationError
from backend_api.models import Movie, UserMovieInteraction

logger = get_logger(__name__)


class UserInteractionService:
    """
    Service for handling user interactions with movies.

    This service encapsulates business logic for tracking user movie interactions
    such as watched status, likes, and watchlist management.

    Following CQRS principles, this service handles commands (state changes)
    while leaving queries (data retrieval) to a separate query class.
    """

    ***REMOVED*** Command methods (write operations)

    def toggle_watchlist(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """
        Toggle a movie in a user's watchlist.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        logger.info(f"Toggling watchlist for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "in_watchlist")

    def toggle_watched(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """
        Toggle a movie as watched by a user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        logger.info(f"Toggling watched status for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "watched")

    def toggle_liked(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """
        Toggle a movie as liked by a user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Updated user movie interaction

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        logger.info(f"Toggling liked status for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, "liked")

    def delete_interaction(self, db: Session, user_id: int, movie_id: int) -> bool:
        """
        Delete a user's interaction with a movie.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            True if interaction was deleted, False if no interaction existed

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        logger.info(f"Deleting interaction for user {user_id} and movie {movie_id}")
        return delete_user_movie_interaction(db, user_id, movie_id)

    def get_interaction(
        self, db: Session, user_id: int, movie_id: int
    ) -> Optional[UserMovieInteraction]:
        """
        Get a user's interaction with a movie.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            UserMovieInteraction if it exists, None otherwise

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        logger.info(f"Getting interaction for user {user_id} and movie {movie_id}")
        return get_user_movie_interaction(db, user_id, movie_id)

    def set_flag(self, db: Session, user_id: int, movie_id: int, flag: str) -> UserMovieInteraction:
        """
        Set a specific flag to True for a user's interaction with a movie.

        This is an idempotent operation - if the flag is already True,
        the interaction is returned unchanged.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID
            flag: Flag to set ('watched', 'liked', or 'in_watchlist')

        Returns:
            Updated user movie interaction

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid or flag is invalid
        """
        ***REMOVED*** Validate flag
        if flag not in ["watched", "liked", "in_watchlist"]:
            raise ValidationError(
                message=f"Invalid flag: {flag}",
                field_errors={"flag": [f"Must be one of: watched, liked, in_watchlist"]},
            )

        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** Get current interaction
        interaction = get_user_movie_interaction(db, user_id, movie_id)

        ***REMOVED*** If already set to True, return unchanged
        if interaction and getattr(interaction, flag):
            logger.info(f"Flag {flag} already set to True for user {user_id} and movie {movie_id}")
            return interaction

        ***REMOVED*** If interaction exists but flag is False, or interaction doesn't exist,
        ***REMOVED*** toggle the flag (which will set it to True)
        logger.info(f"Setting flag {flag} to True for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, flag)

    def unset_flag(
        self, db: Session, user_id: int, movie_id: int, flag: str
    ) -> UserMovieInteraction:
        """
        Set a specific flag to False for a user's interaction with a movie.

        This is an idempotent operation - if the flag is already False or
        the interaction doesn't exist, a representation of the interaction
        with the flag set to False is returned.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID
            flag: Flag to unset ('watched', 'liked', or 'in_watchlist')

        Returns:
            Updated user movie interaction

        Raises:
            ResourceNotFoundError: If movie doesn't exist
            ValidationError: If user_id is invalid or flag is invalid
        """
        ***REMOVED*** Validate flag
        if flag not in ["watched", "liked", "in_watchlist"]:
            raise ValidationError(
                message=f"Invalid flag: {flag}",
                field_errors={"flag": [f"Must be one of: watched, liked, in_watchlist"]},
            )

        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Validate movie exists
        movie = get_movie_by_id(db, movie_id)
        if not movie:
            raise ResourceNotFoundError(
                message=f"Movie with ID {movie_id} not found",
                resource_type="Movie",
                resource_id=movie_id,
            )

        ***REMOVED*** Get current interaction
        interaction = get_user_movie_interaction(db, user_id, movie_id)

        ***REMOVED*** If no interaction or flag already False, return interaction or create a
        ***REMOVED*** representation with the flag set to False
        if not interaction or not getattr(interaction, flag):
            logger.info(f"Flag {flag} already False for user {user_id} and movie {movie_id}")
            if interaction:
                return interaction
            else:
                ***REMOVED*** Create a representation (not saved to DB) with the flag set to False
                return UserMovieInteraction(
                    user_id=user_id,
                    movie_id=movie_id,
                    watched=False,
                    liked=False,
                    in_watchlist=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

        ***REMOVED*** If interaction exists and flag is True, toggle the flag (which will set it to False)
        logger.info(f"Setting flag {flag} to False for user {user_id} and movie {movie_id}")
        return toggle_user_movie_interaction_flag(db, user_id, movie_id, flag)

    ***REMOVED*** Now add convenience methods for each flag type
    def set_watched(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set watched flag to True."""
        return self.set_flag(db, user_id, movie_id, "watched")

    def unset_watched(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set watched flag to False."""
        return self.unset_flag(db, user_id, movie_id, "watched")

    def set_liked(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set liked flag to True."""
        return self.set_flag(db, user_id, movie_id, "liked")

    def unset_liked(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set liked flag to False."""
        return self.unset_flag(db, user_id, movie_id, "liked")

    def set_watchlist(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set in_watchlist flag to True."""
        return self.set_flag(db, user_id, movie_id, "in_watchlist")

    def unset_watchlist(self, db: Session, user_id: int, movie_id: int) -> UserMovieInteraction:
        """Set in_watchlist flag to False."""
        return self.unset_flag(db, user_id, movie_id, "in_watchlist")

    def import_netflix_history(self, db: Session, user_id: int, csv_content: str) -> Dict[str, Any]:
        """
        Import Netflix watch history from CSV content.

        Parses the Netflix CSV export format, matches movie titles to the database,
        and marks matching movies as watched by the specified user.

        Args:
            db: Database session
            user_id: User ID
            csv_content: CSV content as string

        Returns:
            Dict with import statistics including matched and unmatched movies

        Raises:
            ValidationError: If user_id is invalid or CSV format is incorrect
        """
        ***REMOVED*** Validate inputs
        if user_id <= 0:
            raise ValidationError(
                message="Invalid user ID",
                field_errors={"user_id": ["Must be positive"]},
            )

        ***REMOVED*** Initialize tracking variables
        total_entries = 0
        matched_movies = 0
        already_marked_watched = 0
        newly_marked_watched = 0
        unmatched_titles = []

        try:
            ***REMOVED*** Parse CSV
            csv_io = io.StringIO(csv_content)
            reader = csv.reader(csv_io)

            ***REMOVED*** Skip header if present
            ***REMOVED*** Netflix format typically has: Title, Date
            header = next(reader, None)
            if not header or len(header) < 2:
                raise ValidationError(
                    message="Invalid CSV format. Expected Title, Date columns",
                    field_errors={"csv": ["Invalid CSV format"]},
                )

            ***REMOVED*** Process each row
            for row in reader:
                if len(row) < 2:
                    continue  ***REMOVED*** Skip incomplete rows

                total_entries += 1
                title = row[0].strip()
                watch_date_str = row[1].strip()

                ***REMOVED*** Skip empty titles
                if not title:
                    continue

                ***REMOVED*** Search for matching movie in database
                search_pattern = f"%{title}%"
                ***REMOVED*** Use sqlalchemy's direct import to fix typing issues
                from sqlalchemy.sql.expression import desc as sql_desc

                stmt = (
                    select(Movie)
                    .where(func.lower(Movie.title).like(func.lower(search_pattern)))
                    .order_by(sql_desc(func.coalesce(Movie.popularity, 0)))
                    .limit(1)  ***REMOVED*** Limit to one result since we only need the best match
                )

                movie = db.exec(stmt).first()

                if not movie or movie.id is None:
                    unmatched_titles.append(title)
                    continue

                movie_id = movie.id

                ***REMOVED*** Check if already marked as watched
                existing_interaction = get_user_movie_interaction(db, user_id, movie_id)

                if existing_interaction and existing_interaction.watched:
                    already_marked_watched += 1
                else:
                    ***REMOVED*** Mark as watched
                    try:
                        ***REMOVED*** Convert watch date if possible
                        watch_date = None
                        try:
                            watch_date = date_parser.parse(watch_date_str).date()
                        except:
                            ***REMOVED*** If date parsing fails, just use current date
                            pass

                        self.toggle_watched(db, user_id, movie_id)
                        newly_marked_watched += 1
                        matched_movies += 1
                    except Exception as e:
                        ***REMOVED*** Log but continue with next movie
                        logger.error(f"Error marking movie {movie_id} as watched: {str(e)}")
                        continue

            ***REMOVED*** Return results summary
            return {
                "total_entries": total_entries,
                "matched_movies": matched_movies,
                "already_marked_watched": already_marked_watched,
                "newly_marked_watched": newly_marked_watched,
                "unmatched_titles": unmatched_titles,
            }

        except csv.Error as e:
            logger.error(f"CSV parsing error: {str(e)}")
            raise ValidationError(
                message=f"Error parsing CSV file: {str(e)}",
                field_errors={"csv": ["Invalid CSV format"]},
            )
