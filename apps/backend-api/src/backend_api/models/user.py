"""
User model for authentication and user management.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import passlib.hash
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend_api.models.user_interaction import UserMovieInteraction


class User(SQLModel, table=True):
    """
    User model for authentication.

    Attributes:
        id: Unique identifier for the user
        email: Email address (unique)
        hashed_password: Securely hashed password
        username: Optional username
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
        movie_interactions: Relationship to UserMovieInteraction
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    username: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    ***REMOVED*** Relationships
    movie_interactions: List["UserMovieInteraction"] = Relationship(back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plaintext password securely.

        Args:
            password: The plaintext password to hash

        Returns:
            Securely hashed password string
        """
        return str(passlib.hash.bcrypt.hash(password))

    def verify_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the hashed password.

        Args:
            password: The plaintext password to verify

        Returns:
            True if the password matches, False otherwise
        """
        return bool(passlib.hash.bcrypt.verify(password, self.hashed_password))
