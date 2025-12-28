"""Pydantic schemas for screen-oriented API responses."""

from typing import Any

from pydantic import BaseModel, Field


class NavbarLinkData(BaseModel):
    """Data model for individual navbar links."""

    id: str
    label: str
    href: str
    icon: str | None = None
    order: int
    is_active: bool = False
    badge_count: int | None = None
    metadata: dict[str, Any] | None = None


class NavbarData(BaseModel):
    """Data model for navbar content.

    Provides dynamic navigation structure that can be controlled
    from the backend for different app sections and user states.
    """

    brand: dict[str, Any]
    primary_links: list[NavbarLinkData]
    secondary_links: list[NavbarLinkData]
    user_links: list[NavbarLinkData]
    mobile_menu: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class HomeScreenData(BaseModel):
    """Data model for home screen.

    Aggregates multiple data sources for the main app home screen including
    featured content, popular movies, recent releases, and personalized recommendations.
    """

    featured_movies: list[dict[str, Any]]
    popular_movies: list[dict[str, Any]]
    recent_releases: list[dict[str, Any]]
    user_recommendations: list[dict[str, Any]]
    genres: list[dict[str, Any]]


class UserInteractions(BaseModel):
    """User interaction data for a movie."""

    in_watchlist: bool = Field(
        default=False, description="Whether the movie is in user's watchlist"
    )
    is_favorite: bool = Field(default=False, description="Whether the movie is marked as favorite")
    user_rating: float | None = Field(default=None, description="User's rating for the movie")
    watch_progress: float = Field(default=0, description="User's watch progress (0-100)")
    is_watched: bool = Field(default=False, description="Whether the movie has been watched")


class MovieListData(BaseModel):
    """Paginated movie list data."""

    total: int = Field(..., description="Total number of movies")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    results: list[dict[str, Any]] = Field(..., description="List of movies")


class GenreScreenData(BaseModel):
    """Data model for genre screen.

    Shows movies filtered by specific genre with pagination support.
    """

    genre: dict[str, Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: list[dict[str, Any]]


class SidebarLinkData(BaseModel):
    """Schema for sidebar navigation links."""

    id: str = Field(..., description="Unique identifier for the link")
    label: str = Field(..., description="Display text for the link")
    href: str = Field(..., description="URL path for the link")
    icon: str | None = Field(None, description="Icon identifier for the link")


class SidebarFilters(BaseModel):
    """Schema for sidebar filter configuration."""

    show: bool = Field(True, description="Whether to show the filter section")
    defaults: dict[str, Any] = Field(
        default_factory=dict,
        description="Default filter values",
    )
    locked: list[str] = Field(
        default_factory=list,
        description="List of filter keys that cannot be changed",
    )


class SidebarGenre(BaseModel):
    """Schema for sidebar genre links."""

    id: int = Field(..., description="Genre ID")
    name: str = Field(..., description="Genre name")
    href: str = Field(..., description="URL path for the genre")


class SidebarMetadata(BaseModel):
    """Schema for sidebar metadata."""

    layout: str = Field("sidebar", description="Layout type")
    version: str = Field(..., description="API version")
    user_authenticated: bool = Field(..., description="Whether user is authenticated")


class SidebarData(BaseModel):
    """Schema for complete sidebar data."""

    home: dict[str, str] = Field(
        ...,
        description="Home link configuration",
    )
    user_links: list[SidebarLinkData] = Field(
        default_factory=list,
        description="User-specific navigation links",
    )
    top_links: list[SidebarLinkData] = Field(
        ...,
        description="Top movies navigation links",
    )
    filters: SidebarFilters = Field(
        ...,
        description="Filter configuration",
    )
    genres: list[SidebarGenre] = Field(
        ...,
        description="Genre navigation links",
    )
    metadata: SidebarMetadata = Field(
        ...,
        description="Sidebar metadata",
    )


class ActorScreenData(BaseModel):
    """Aggregated data for actor detail screen."""

    actor: dict[str, Any] = Field(..., description="Actor details")
    movies: MovieListData = Field(..., description="Actor's movies with pagination")
