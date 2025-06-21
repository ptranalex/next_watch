"""FastAPI-specific configuration utilities.

This module provides configuration classes and utilities specifically
designed for FastAPI applications, extending the base config library.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from config.base.config import ServiceConfig


class FastAPIConfigMixin(BaseModel):
    """Mixin for FastAPI-specific configuration.

    This mixin adds FastAPI-specific configuration options to a ServiceConfig.
    """

    ***REMOVED*** API documentation
    docs_url: Optional[str] = Field(
        default="/docs", description="URL for Swagger UI documentation (None to disable)"
    )
    redoc_url: Optional[str] = Field(
        default="/redoc", description="URL for ReDoc documentation (None to disable)"
    )
    openapi_url: Optional[str] = Field(
        default="/openapi.json", description="URL for OpenAPI schema (None to disable)"
    )

    ***REMOVED*** CORS configuration (additional to base ServiceConfig)
    cors_allow_credentials: bool = Field(
        default=True, description="Allow credentials for CORS requests"
    )
    cors_allow_methods: List[str] = Field(
        default=["*"], description="List of allowed HTTP methods for CORS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], description="List of allowed HTTP headers for CORS"
    )

    ***REMOVED*** Performance
    workers: int = Field(default=1, description="Number of worker processes")
    keepalive: int = Field(default=65, description="Keep-alive timeout")

    @validator("workers")
    def validate_workers_positive(cls, v: int) -> int:
        """Validate that workers count is positive."""
        if v < 1:
            raise ValueError("Workers count must be at least 1")
        return v


class FastAPIConfig(ServiceConfig, FastAPIConfigMixin):
    """Complete FastAPI service configuration.

    This class combines the base ServiceConfig with FastAPI-specific options.
    """

    def get_fastapi_kwargs(self) -> Dict[str, Any]:
        """Get keyword arguments for FastAPI constructor.

        Returns:
            Dictionary of keyword arguments for FastAPI
        """
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "redoc_url": self.redoc_url,
            "openapi_url": self.openapi_url,
            "title": self.service_name,
            "description": getattr(self, "description", f"API for {self.service_name}"),
            "version": self.version,
        }

    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration.

        Returns:
            Dictionary of CORS configuration options
        """
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers,
        }

    def get_uvicorn_config(self) -> Dict[str, Any]:
        """Get Uvicorn configuration.

        Returns:
            Dictionary of Uvicorn configuration options
        """
        return {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "reload": self.debug,
            "log_level": self.log_level.lower(),
            "timeout_keep_alive": self.keepalive,
        }
