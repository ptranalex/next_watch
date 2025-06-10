"""
Main FastAPI application for the Next Watch Authentication Service.

Dedicated microservice for authentication and token management.
"""

import os
import logging

***REMOVED*** Setup logging early
from auth_api.core.logging import setup_logging

setup_logging()

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Create application instance
from auth_api.core import create_app

app = create_app()
