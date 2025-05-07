"""
User movie interaction service module.

This service handles business logic related to how users interact with movies,
including tracking movies as watched, liked, and in watchlists.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from sqlmodel import Session, select
from sqlalchemy import func, desc, nullslast
import csv
import io
from dateutil import parser as date_parser  ***REMOVED*** type: ignore

from movie_storage.models import UserMovieInteraction, User, Movie
from movie_storage.db.operations import (
    get_movie_by_id,
    get_user_movie_interaction,
    create_user_movie_interaction,
    update_user_movie_interaction,
    delete_user_movie_interaction,
    toggle_user_movie_interaction_flag,
)
from backend_api.errors import ResourceNotFoundError, ValidationError, ServiceError

logger = logging.getLogger(__name__)


class UserInteractionService:
    """
    Service for handling user interactions with movies.

    This service encapsulates business logic for tracking user movie interactions
    such as watched status, likes, and watchlist management.

    Following CQRS principles, this service handles commands (state changes)
    while leaving queries (data retrieval) to a separate query class.
    """

    ***REMOVED*** Command methods (write operations)

    def toggle_watchlist(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
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

    def toggle_watched(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
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

    def toggle_liked(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction:
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

    def import_netflix_history(
        self, db: Session, user_id: int, csv_content: str
    ) -> Dict[str, Any]:
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
                stmt = (
                    select(Movie)
                    .where(func.lower(Movie.title).like(func.lower(search_pattern)))
                    .order_by(nullslast(desc(Movie.popularity)), Movie.id)  ***REMOVED*** type: ignore
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
                        logger.error(
                            f"Error marking movie {movie_id} as watched: {str(e)}"
                        )
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
