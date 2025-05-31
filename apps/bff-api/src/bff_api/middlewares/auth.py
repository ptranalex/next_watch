"""Authentication middleware for BFF application."""

import logging
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication."""

    def __init__(self, app, jwt_secret: Optional[str] = None):
        """Initialize auth middleware.

        Args:
            app: FastAPI application
            jwt_secret: JWT secret for token validation
        """
        super().__init__(app)
        self.jwt_secret = jwt_secret

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and validate authentication.

        Args:
            request: FastAPI request
            call_next: Next middleware function

        Returns:
            Response from next middleware/endpoint or auth error
        """
        ***REMOVED*** Skip auth for health endpoints, public routes, and OPTIONS requests (CORS preflight)
        if request.url.path.startswith("/health") or request.url.path == "/" or request.method == "OPTIONS":
            return await call_next(request)

        ***REMOVED*** Extract authorization header
        auth_header = request.headers.get("authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  ***REMOVED*** Remove "Bearer " prefix

            ***REMOVED*** TODO: Implement JWT token validation
            ***REMOVED*** For now, just pass through
            user_id = self._validate_token(token)

            ***REMOVED*** Add user info to request state
            request.state.user_id = user_id
            request.state.authenticated = user_id is not None
        else:
            ***REMOVED*** No auth header - proceed as anonymous user
            request.state.user_id = None
            request.state.authenticated = False

        return await call_next(request)

    def _validate_token(self, token: str) -> Optional[int]:
        """Validate JWT token and extract user ID.

        Args:
            token: JWT token

        Returns:
            User ID if token is valid, None otherwise
        """
        ***REMOVED*** TODO: Implement actual JWT validation
        ***REMOVED*** For now, return None (anonymous)
        return None
