"""Pydantic schemas for screen-oriented API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NavbarLinkData(BaseModel):
    """Data model for individual navbar links."""

    id: str
    label: str
    href: str
    icon: Optional[str] = None
    order: int
    is_active: bool = False
    badge_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class NavbarData(BaseModel):
    """Data model for navbar content.

    Provides dynamic navigation structure that can be controlled
    from the backend for different app sections and user states.
    """

    brand: Dict[str, Any]
    primary_links: List[NavbarLinkData]
    secondary_links: List[NavbarLinkData]
    user_links: List[NavbarLinkData]
    mobile_menu: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class HomeScreenData(BaseModel):
    """Data model for home screen.

    Aggregates multiple data sources for the main app home screen including
    featured content, popular movies, recent releases, and personalized recommendations.
    """

    featured_movies: List[Dict[str, Any]]
    popular_movies: List[Dict[str, Any]]
    recent_releases: List[Dict[str, Any]]
    user_recommendations: List[Dict[str, Any]]
    genres: List[Dict[str, Any]]


class UserInteractions(BaseModel):
    """User interaction data for a movie."""

    in_watchlist: bool = Field(
        default=False, description="Whether the movie is in user's watchlist"
    )
    is_favorite: bool = Field(default=False, description="Whether the movie is marked as favorite")
    user_rating: Optional[float] = Field(default=None, description="User's rating for the movie")
    watch_progress: float = Field(default=0, description="User's watch progress (0-100)")
    is_watched: bool = Field(default=False, description="Whether the movie has been watched")


class MovieScreenData(BaseModel):
    """Aggregated data for movie detail screen."""

    movie: Dict[str, Any] = Field(..., description="Movie details")
    cast: List[Dict[str, Any]] = Field(default_factory=list, description="Movie cast")
    trailers: List[Dict[str, Any]] = Field(default_factory=list, description="Movie trailers")
    similar_movies: List[Dict[str, Any]] = Field(default_factory=list, description="Similar movies")
    user_interactions: UserInteractions = Field(
        default_factory=UserInteractions, description="User interaction data"
    )


class MovieListData(BaseModel):
    """Paginated movie list data."""

    total: int = Field(..., description="Total number of movies")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    results: List[Dict[str, Any]] = Field(..., description="List of movies")


class GenreScreenData(BaseModel):
    """Data model for genre screen.

    Shows movies filtered by specific genre with pagination support.
    """

    genre: Dict[str, Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    results: List[Dict[str, Any]]


class SidebarLinkData(BaseModel):
    """Schema for sidebar navigation links."""

    id: str = Field(..., description="Unique identifier for the link")
    label: str = Field(..., description="Display text for the link")
    href: str = Field(..., description="URL path for the link")
    icon: Optional[str] = Field(None, description="Icon identifier for the link")


class SidebarFilters(BaseModel):
    """Schema for sidebar filter configuration."""

    show: bool = Field(True, description="Whether to show the filter section")
    defaults: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default filter values",
    )
    locked: List[str] = Field(
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

    home: Dict[str, str] = Field(
        ...,
        description="Home link configuration",
    )
    user_links: List[SidebarLinkData] = Field(
        default_factory=list,
        description="User-specific navigation links",
    )
    top_links: List[SidebarLinkData] = Field(
        ...,
        description="Top movies navigation links",
    )
    filters: SidebarFilters = Field(
        ...,
        description="Filter configuration",
    )
    genres: List[SidebarGenre] = Field(
        ...,
        description="Genre navigation links",
    )
    metadata: SidebarMetadata = Field(
        ...,
        description="Sidebar metadata",
    )


class ActorScreenData(BaseModel):
    """Aggregated data for actor detail screen."""

    actor: Dict[str, Any] = Field(..., description="Actor details")
    movies: MovieListData = Field(..., description="Actor's movies with pagination")
