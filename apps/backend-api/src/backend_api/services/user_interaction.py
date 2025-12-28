"""
User movie interaction service module.

This service handles business logic related to how users interact with movies,
including tracking movies as watched, liked, and in watchlists.
"""

import csv
import io
from datetime import datetime
from typing import Any

from config.logging import get_logger
from dateutil import parser as date_parser
from sqlalchemy import func
from sqlmodel import Session, select

from backend_api.db.operations import (
    create_user_movie_interaction,
    delete_user_movie_interaction,
    get_movie_by_id,
    get_user_movie_interaction,
)
from backend_api.errors import ResourceNotFoundError, ValidationError
from backend_api.models import Movie, UserMovieInteraction

logger = get_logger(__name__)

***REMOVED*** Cache invalidation is handled by short TTL on user interactions in BFF API


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

        ***REMOVED*** Get current interaction
        interaction = get_user_movie_interaction(db, user_id, movie_id)

        ***REMOVED*** If no interaction exists, create one with in_watchlist=True
        if not interaction:
            result = create_user_movie_interaction(db, user_id, movie_id, in_watchlist=True)
            return result

        ***REMOVED*** Toggle the watchlist flag
        interaction.in_watchlist = not interaction.in_watchlist
        interaction.updated_at = datetime.utcnow()

        ***REMOVED*** Keep the interaction even if all flags are False to maintain history
        ***REMOVED*** This ensures that operations work correctly even if the movie was previously unmarked

        ***REMOVED*** Save changes to database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

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

        ***REMOVED*** Get current interaction
        interaction = get_user_movie_interaction(db, user_id, movie_id)

        ***REMOVED*** If no interaction exists, create one with watched=True
        if not interaction:
            result = create_user_movie_interaction(db, user_id, movie_id, watched=True)
            return result

        ***REMOVED*** Toggle the watched flag
        interaction.watched = not interaction.watched
        interaction.updated_at = datetime.utcnow()

        ***REMOVED*** Keep the interaction even if all flags are False to maintain history
        ***REMOVED*** This ensures that operations work correctly even if the movie was previously unmarked

        ***REMOVED*** Save changes to database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

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

        ***REMOVED*** Get current interaction
        interaction = get_user_movie_interaction(db, user_id, movie_id)

        ***REMOVED*** If no interaction exists, create one with liked=True
        if not interaction:
            result = create_user_movie_interaction(db, user_id, movie_id, liked=True)
            return result

        ***REMOVED*** Toggle the liked flag
        interaction.liked = not interaction.liked
        interaction.updated_at = datetime.utcnow()

        ***REMOVED*** Keep the interaction even if all flags are False to maintain history
        ***REMOVED*** This ensures that operations work correctly even if the movie was previously unmarked

        ***REMOVED*** Save changes to database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

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
        result = delete_user_movie_interaction(db, user_id, movie_id)

        return result

    def get_interaction(
        self, db: Session, user_id: int, movie_id: int
    ) -> UserMovieInteraction | None:
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

        return get_user_movie_interaction(db, user_id, movie_id)

    def set_flag(self, db: Session, user_id: int, movie_id: int, flag: str) -> UserMovieInteraction:
        """
        Set a specific flag to True for a user's movie interaction.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID
            flag: Flag to set ("watched", "liked", "in_watchlist")

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
                field_errors={"flag": ["Must be one of: watched, liked, in_watchlist"]},
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

        ***REMOVED*** If no interaction exists, create one with the flag set to True
        if not interaction:
            logger.info(
                f"Creating interaction with {flag}=True for user {user_id} and movie {movie_id}"
            )
            kwargs = {flag: True}
            result = create_user_movie_interaction(db, user_id, movie_id, **kwargs)
            return result

        ***REMOVED*** If flag is already True, return as-is
        if getattr(interaction, flag):
            logger.info(f"Flag {flag} already True for user {user_id} and movie {movie_id}")
            return interaction

        ***REMOVED*** Set the flag to True directly on the interaction object
        logger.info(f"Setting flag {flag} to True for user {user_id} and movie {movie_id}")
        setattr(interaction, flag, True)
        interaction.updated_at = datetime.utcnow()

        ***REMOVED*** Save changes to database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

    def unset_flag(
        self, db: Session, user_id: int, movie_id: int, flag: str
    ) -> UserMovieInteraction:
        """
        Set a specific flag to False for a user's movie interaction.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID
            flag: Flag to unset ("watched", "liked", "in_watchlist")

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
                field_errors={"flag": ["Must be one of: watched, liked, in_watchlist"]},
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

        ***REMOVED*** If no interaction exists, create a representation with the flag set to False
        if not interaction:
            logger.info(f"No interaction exists for user {user_id} and movie {movie_id}")
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

        ***REMOVED*** If flag is already False, return as-is
        if not getattr(interaction, flag):
            logger.info(f"Flag {flag} already False for user {user_id} and movie {movie_id}")
            return interaction

        ***REMOVED*** Set the flag to False directly on the interaction object
        logger.info(f"Setting flag {flag} to False for user {user_id} and movie {movie_id}")
        setattr(interaction, flag, False)
        interaction.updated_at = datetime.utcnow()

        ***REMOVED*** Keep the interaction even if all flags are False to maintain history
        ***REMOVED*** This ensures that operations like "remove from watchlist" work correctly
        ***REMOVED*** even if the movie was previously unmarked from all collections

        ***REMOVED*** Save changes to database
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

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

    ***REMOVED*** ============================================================================
    ***REMOVED*** NEW COLLECTION-ORIENTED METHODS
    ***REMOVED*** ============================================================================

    def add_to_watchlist(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Add a movie to user's watchlist.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_created) where was_created indicates if this was a new addition

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

        ***REMOVED*** Check if already in watchlist
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if existing_interaction and existing_interaction.in_watchlist:
            logger.info(f"Movie {movie_id} already in watchlist for user {user_id}")
            return existing_interaction, False

        ***REMOVED*** Add to watchlist
        logger.info(f"Adding movie {movie_id} to watchlist for user {user_id}")
        interaction = self.set_watchlist(db, user_id, movie_id)
        return interaction, True

    def remove_from_watchlist(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Remove a movie from user's watchlist.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_removed) where was_removed indicates if movie was actually removed

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

        ***REMOVED*** Check if in watchlist
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if not existing_interaction or not existing_interaction.in_watchlist:
            logger.info(f"Movie {movie_id} not in watchlist for user {user_id}")
            return (
                existing_interaction
                or UserMovieInteraction(
                    user_id=user_id,
                    movie_id=movie_id,
                    watched=False,
                    liked=False,
                    in_watchlist=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                False,
            )

        ***REMOVED*** Remove from watchlist
        logger.info(f"Removing movie {movie_id} from watchlist for user {user_id}")
        interaction = self.unset_watchlist(db, user_id, movie_id)
        return interaction, True

    def mark_as_watched(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Mark a movie as watched by user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_created) where was_created indicates if this was newly marked

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

        ***REMOVED*** Check if already watched
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if existing_interaction and existing_interaction.watched:
            logger.info(f"Movie {movie_id} already watched by user {user_id}")
            return existing_interaction, False

        ***REMOVED*** Mark as watched
        logger.info(f"Marking movie {movie_id} as watched for user {user_id}")
        interaction = self.set_watched(db, user_id, movie_id)
        return interaction, True

    def unmark_as_watched(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Unmark a movie as watched by user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_removed) where was_removed indicates if watch status was actually removed

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

        ***REMOVED*** Check if watched
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if not existing_interaction or not existing_interaction.watched:
            logger.info(f"Movie {movie_id} not watched by user {user_id}")
            return (
                existing_interaction
                or UserMovieInteraction(
                    user_id=user_id,
                    movie_id=movie_id,
                    watched=False,
                    liked=False,
                    in_watchlist=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                False,
            )

        ***REMOVED*** Unmark as watched
        logger.info(f"Unmarking movie {movie_id} as watched for user {user_id}")
        interaction = self.unset_watched(db, user_id, movie_id)
        return interaction, True

    def like_movie(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Like a movie for user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_created) where was_created indicates if this was newly liked

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

        ***REMOVED*** Check if already liked
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if existing_interaction and existing_interaction.liked:
            logger.info(f"Movie {movie_id} already liked by user {user_id}")
            return existing_interaction, False

        ***REMOVED*** Like movie
        logger.info(f"Liking movie {movie_id} for user {user_id}")
        interaction = self.set_liked(db, user_id, movie_id)
        return interaction, True

    def unlike_movie(
        self, db: Session, user_id: int, movie_id: int
    ) -> tuple[UserMovieInteraction, bool]:
        """
        Unlike a movie for user.

        Args:
            db: Database session
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Tuple of (interaction, was_removed) where was_removed indicates if like was actually removed

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

        ***REMOVED*** Check if liked
        existing_interaction = get_user_movie_interaction(db, user_id, movie_id)
        if not existing_interaction or not existing_interaction.liked:
            logger.info(f"Movie {movie_id} not liked by user {user_id}")
            return (
                existing_interaction
                or UserMovieInteraction(
                    user_id=user_id,
                    movie_id=movie_id,
                    watched=False,
                    liked=False,
                    in_watchlist=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                False,
            )

        ***REMOVED*** Unlike movie
        logger.info(f"Unliking movie {movie_id} for user {user_id}")
        interaction = self.unset_liked(db, user_id, movie_id)
        return interaction, True

    def import_netflix_history(self, db: Session, user_id: int, csv_content: str) -> dict[str, Any]:
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
                        try:
                            date_parser.parse(watch_date_str).date()
                        except Exception:
                            ***REMOVED*** If date parsing fails, just use current date
                            pass

                        ***REMOVED*** Use the toggle_watched method
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
