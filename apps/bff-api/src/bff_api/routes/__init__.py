"""Routes package for BFF API application.

This package contains all the API endpoints (routes) for the BFF API service,
organized by version and resource type. The routes follow REST conventions and
are structured around resources rather than actions.

The API uses URL-based versioning with the `/api/v{n}/` prefix, with each version
having its own package of route modules. This enables the API to evolve while
maintaining backward compatibility.

Key components:
- api_v1.py: Aggregates all v1 API routes
- v1/: Directory containing resource-specific route modules for API v1
- health.py: Health check endpoints (at root level, not versioned)
- meta.py: Meta endpoints for service information

Routes use FastAPI's dependency injection system to access services and
follow consistent patterns for documentation, validation, and error handling.

See the README.md file in this directory for detailed documentation.
"""

from bff_api.routes.api_v1 import api_v1_router
from bff_api.routes.health import router as health_router

__all__ = ["api_v1_router", "health_router"]
