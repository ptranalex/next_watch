"""Pydantic schemas for BFF API requests and responses.

This module defines all data models (schemas) used for request validation,
response serialization, and data transfer between components. These schemas
are implemented using Pydantic models, which provide runtime type checking,
data validation, and automatic OpenAPI schema generation.

The schemas are organized by domain:
- auth_schemas.py: Authentication and authorization schemas
- screen_schemas.py: Movie, TV show, and media content schemas
- user_interaction_schemas.py: User ratings, reviews, and interactions schemas

All schemas follow consistent patterns for validation, inheritance, and documentation,
with appropriate separation between input and output models.

See the README.md file in this directory for detailed documentation.
"""

from bff_api.schemas.auth_schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from bff_api.schemas.screen_schemas import (
    GenreScreenData,
    HomeScreenData,
    MovieListData,
    MovieScreenData,
    NavbarData,
    NavbarLinkData,
)
from bff_api.schemas.user_interaction_schemas import (
    ToggleInteractionRequest,
    ToggleInteractionResponse,
    UserMovieInteractionResponse,
    UserMovieInteractionUpdate,
)

__all__ = [
    ***REMOVED*** Screen data schemas
    "HomeScreenData",
    "MovieScreenData",
    "MovieListData",
    "GenreScreenData",
    "NavbarData",
    "NavbarLinkData",
    ***REMOVED*** User interaction schemas
    "UserMovieInteractionResponse",
    "UserMovieInteractionUpdate",
    "ToggleInteractionRequest",
    "ToggleInteractionResponse",
    ***REMOVED*** Authentication schemas
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
]
