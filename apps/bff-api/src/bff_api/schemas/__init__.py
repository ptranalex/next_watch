"""Pydantic schemas for BFF API responses."""

from bff_api.schemas.screen_schemas import (
    HomeScreenData,
    MovieScreenData,
    MovieListData,
    GenreScreenData,
    NavbarData,
    NavbarLinkData,
)
from bff_api.schemas.user_interaction_schemas import (
    UserMovieInteractionResponse,
    UserMovieInteractionUpdate,
    ToggleInteractionRequest,
    ToggleInteractionResponse,
)

__all__ = [
    "HomeScreenData",
    "MovieScreenData",
    "MovieListData",
    "GenreScreenData",
    "NavbarData",
    "NavbarLinkData",
    "UserMovieInteractionResponse",
    "UserMovieInteractionUpdate",
    "ToggleInteractionRequest",
    "ToggleInteractionResponse",
]
