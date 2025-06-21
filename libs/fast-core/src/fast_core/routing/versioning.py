"""API versioning utilities for FastAPI routing.

This module provides utilities for handling API versioning in FastAPI applications,
supporting both URL path and header-based versioning strategies.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.routing import APIRoute


class VersioningStrategy(str, Enum):
    """API versioning strategy options."""

    URL_PATH = "url_path"
    HEADER = "header"
    QUERY_PARAM = "query_param"
    ACCEPT_HEADER = "accept_header"


class APIVersion:
    """API version representation."""

    def __init__(
        self,
        major: int,
        minor: int = 0,
        patch: int = 0,
        label: Optional[str] = None,
    ):
        """Initialize API version.

        Args:
            major: Major version number
            minor: Minor version number
            patch: Patch version number
            label: Optional version label (e.g., "beta", "alpha")
        """
        self.major = major
        self.minor = minor
        self.patch = patch
        self.label = label

    def __str__(self) -> str:
        """String representation of version."""
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.label:
            version_str += f"-{self.label}"
        return version_str

    def __repr__(self) -> str:
        """Representation of version."""
        return f"APIVersion({self.major}, {self.minor}, {self.patch}, {self.label!r})"

    def __eq__(self, other: Any) -> bool:
        """Check version equality."""
        if not isinstance(other, APIVersion):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.label == other.label
        )

    def __lt__(self, other: "APIVersion") -> bool:
        """Compare versions."""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        ***REMOVED*** Labels are compared lexicographically, None is considered "latest"
        if self.label is None and other.label is not None:
            return False
        if self.label is not None and other.label is None:
            return True
        return (self.label or "") < (other.label or "")

    def to_short_string(self) -> str:
        """Get short version string (major.minor)."""
        return f"{self.major}.{self.minor}"

    def to_path_prefix(self) -> str:
        """Get path prefix for URL versioning."""
        return f"v{self.major}.{self.minor}"

    @classmethod
    def from_string(cls, version_str: str) -> "APIVersion":
        """Parse version from string.

        Args:
            version_str: Version string (e.g., "1.0.0", "2.1.0-beta")

        Returns:
            APIVersion instance

        Raises:
            ValueError: If version string is invalid
        """
        ***REMOVED*** Remove 'v' prefix if present
        if version_str.startswith("v"):
            version_str = version_str[1:]

        ***REMOVED*** Split by label separator
        if "-" in version_str:
            version_part, label = version_str.split("-", 1)
        else:
            version_part, label = version_str, None

        ***REMOVED*** Parse version numbers
        parts = version_part.split(".")
        if len(parts) < 1 or len(parts) > 3:
            raise ValueError(f"Invalid version format: {version_str}")

        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except ValueError:
            raise ValueError(f"Invalid version format: {version_str}")

        return cls(major=major, minor=minor, patch=patch, label=label)


class VersionedRouter:
    """Router with versioning support."""

    def __init__(
        self,
        strategy: VersioningStrategy = VersioningStrategy.URL_PATH,
        header_name: str = "API-Version",
        query_param_name: str = "version",
        default_version: Optional[APIVersion] = None,
    ):
        """Initialize versioned router.

        Args:
            strategy: Versioning strategy to use
            header_name: Header name for header-based versioning
            query_param_name: Query parameter name for query-based versioning
            default_version: Default version if not specified
        """
        self.strategy = strategy
        self.header_name = header_name
        self.query_param_name = query_param_name
        self.default_version = default_version or APIVersion(1, 0, 0)
        self.routers: Dict[str, APIRouter] = {}

    def get_router(self, version: Union[str, APIVersion]) -> APIRouter:
        """Get or create router for specific version.

        Args:
            version: API version

        Returns:
            APIRouter for the specified version
        """
        if isinstance(version, str):
            version = APIVersion.from_string(version)

        version_key = str(version)
        if version_key not in self.routers:
            prefix = ""
            if self.strategy == VersioningStrategy.URL_PATH:
                prefix = f"/{version.to_path_prefix()}"

            self.routers[version_key] = APIRouter(
                prefix=prefix,
                tags=[f"v{version.major}.{version.minor}"],
            )

        return self.routers[version_key]

    def include_versioned_router(
        self,
        app_router: APIRouter,
        version: Union[str, APIVersion],
        router: APIRouter,
    ) -> None:
        """Include a versioned router in the main app router.

        Args:
            app_router: Main application router
            version: API version
            router: Router to include
        """
        if isinstance(version, str):
            version = APIVersion.from_string(version)

        if self.strategy == VersioningStrategy.URL_PATH:
            prefix = f"/{version.to_path_prefix()}"
            app_router.include_router(
                router,
                prefix=prefix,
                tags=[f"v{version.major}.{version.minor}"],
            )
        else:
            ***REMOVED*** For non-URL strategies, include without prefix
            app_router.include_router(
                router,
                tags=[f"v{version.major}.{version.minor}"],
            )

    def get_version_from_request(self, request: Request) -> APIVersion:
        """Extract version from request based on strategy.

        Args:
            request: FastAPI request

        Returns:
            APIVersion extracted from request

        Raises:
            HTTPException: If version is invalid or not found
        """
        if self.strategy == VersioningStrategy.URL_PATH:
            ***REMOVED*** Extract from URL path
            path_parts = request.url.path.strip("/").split("/")
            for part in path_parts:
                if part.startswith("v") and len(part) > 1:
                    try:
                        return APIVersion.from_string(part)
                    except ValueError:
                        continue
            return self.default_version

        elif self.strategy == VersioningStrategy.HEADER:
            ***REMOVED*** Extract from header
            version_str = request.headers.get(self.header_name)
            if not version_str:
                return self.default_version
            try:
                return APIVersion.from_string(version_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid version format in {self.header_name} header: {version_str}",
                )

        elif self.strategy == VersioningStrategy.QUERY_PARAM:
            ***REMOVED*** Extract from query parameter
            version_str = request.query_params.get(self.query_param_name)
            if not version_str:
                return self.default_version
            try:
                return APIVersion.from_string(version_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid version format in {self.query_param_name} parameter: {version_str}",
                )

        elif self.strategy == VersioningStrategy.ACCEPT_HEADER:
            ***REMOVED*** Extract from Accept header
            accept_header = request.headers.get("Accept", "")
            ***REMOVED*** Look for version in Accept header like: application/vnd.api+json;version=1.0
            for part in accept_header.split(","):
                part = part.strip()
                if "version=" in part:
                    version_str = part.split("version=")[1].split(";")[0].strip()
                    try:
                        return APIVersion.from_string(version_str)
                    except ValueError:
                        continue
            return self.default_version

        return self.default_version


def version_dependency(
    versioned_router: VersionedRouter,
) -> Callable:
    """Create version dependency for route handlers.

    Args:
        versioned_router: Versioned router instance

    Returns:
        Dependency function that extracts version from request
    """

    def get_version(request: Request) -> APIVersion:
        return versioned_router.get_version_from_request(request)

    return get_version


def version_header_dependency(
    header_name: str = "API-Version",
    default_version: str = "1.0.0",
) -> Callable:
    """Create header-based version dependency.

    Args:
        header_name: Name of the version header
        default_version: Default version string

    Returns:
        Dependency function that extracts version from header
    """

    def get_version(version_header: Optional[str] = Header(None, alias=header_name)) -> APIVersion:
        if not version_header:
            return APIVersion.from_string(default_version)
        try:
            return APIVersion.from_string(version_header)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid version format: {version_header}",
            )

    return get_version


def deprecation_warning_middleware(
    deprecated_versions: List[str],
    sunset_date: Optional[str] = None,
) -> Callable:
    """Create middleware to add deprecation warnings.

    Args:
        deprecated_versions: List of deprecated version strings
        sunset_date: Optional sunset date for deprecated versions

    Returns:
        Middleware function
    """

    async def middleware(request: Request, call_next: Callable) -> Any:
        response = await call_next(request)

        ***REMOVED*** Check if current version is deprecated
        ***REMOVED*** This is a simplified check - in practice you'd extract version from request
        version_str = request.headers.get("API-Version", "1.0.0")
        if version_str in deprecated_versions:
            response.headers["Warning"] = f'299 - "API version {version_str} is deprecated"'
            if sunset_date:
                response.headers["Sunset"] = sunset_date

        return response

    return middleware
