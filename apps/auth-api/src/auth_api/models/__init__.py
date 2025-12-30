"""Model definitions for the auth API."""

# Re-export all models from their respective modules
from auth_api.models.user import User

__all__: list[str] = [
    "User",
]
