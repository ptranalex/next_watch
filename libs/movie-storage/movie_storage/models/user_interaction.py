"""
User Movie Interactions model for tracking user engagement with movies.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from movie_storage.models.movie import Movie
    from movie_storage.models.user import User


class UserMovieInteraction(SQLModel, table=True):
    """
    User Movie Interaction model for tracking how users interact with movies.

    Attributes:
        id: Unique identifier for the interaction
        user_id: Foreign key to the user
        movie_id: Foreign key to the movie
        watched: Whether the user has watched the movie
        liked: Whether the user has liked the movie
        in_watchlist: Whether the movie is in the user's watchlist
        created_at: Timestamp when the interaction was created
        updated_at: Timestamp when the interaction was last updated
    """

    __tablename__ = "user_movie_interactions"

    ***REMOVED*** Table constraints
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_user_movie_interaction"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    movie_id: int = Field(foreign_key="movie.id", index=True)

    ***REMOVED*** Interaction flags
    watched: bool = Field(default=False)
    liked: bool = Field(default=False)
    in_watchlist: bool = Field(default=False)

    ***REMOVED*** Timestamp fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    ***REMOVED*** Relationships - avoid circular imports with TYPE_CHECKING
    user: "User" = Relationship(back_populates="movie_interactions")
    movie: "Movie" = Relationship(back_populates="user_interactions")
