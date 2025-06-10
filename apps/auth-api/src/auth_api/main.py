"""
Main FastAPI application for the Next Watch Authentication Service.

Dedicated microservice for authentication and token management.
"""

import os
import logging
from pathlib import Path

***REMOVED*** Load environment variables FIRST - before any config imports
from auth_api.config.env import load_environment_variables

***REMOVED*** Explicitly set the project root to the auth-api directory
***REMOVED*** This prevents loading .env files from parent directories
auth_api_root = Path(__file__).parent.parent.parent  ***REMOVED*** main.py -> auth_api -> src -> auth-api/

***REMOVED*** Load .env files at application startup
try:
    env_loaded = load_environment_variables(project_root=auth_api_root)
    if env_loaded:
        print("✅ Environment variables loaded successfully from .env files")
        print(f"📁 Project root: {auth_api_root}")
    else:
        print("⚠️  No .env files found, using system environment variables only")
except Exception as e:
    print(f"❌ Error loading environment variables: {e}")
    print("Using system environment variables only")

***REMOVED*** Debug: Check DATABASE_URL immediately after loading
database_url_from_env = os.getenv("DATABASE_URL")
print(f"🔍 DEBUG: DATABASE_URL from environment: {database_url_from_env}")

***REMOVED*** Setup logging early (now with proper env vars loaded)
from auth_api.core.logging import setup_logging

setup_logging()

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Create application instance
from auth_api.core import create_app

app = create_app()
