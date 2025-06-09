"""Main FastAPI application for BFF service."""

import os
import logging
from pathlib import Path

***REMOVED*** Load environment variables
try:
    from dotenv import load_dotenv

    ***REMOVED*** Only load .env files if we're not in production
    if os.getenv("ENVIRONMENT") != "production":
        ***REMOVED*** Try multiple locations to find .env files (prioritize current directory)
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd() / ".env.local",
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3] / ".env.local",
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
                break
except ImportError:
    pass  ***REMOVED*** Continue without dotenv if not installed

***REMOVED*** Import configuration after environment variables are loaded
from bff_api.config.app import settings
from bff_api.core.logging import setup_logging

***REMOVED*** Configure logging early
setup_logging(
    log_level=settings.log_level,
    verbose=settings.debug,
    quiet=False,
)

***REMOVED*** Get logger for this module
logger = logging.getLogger(__name__)

***REMOVED*** Log environment
logger.info(f"Running in environment: {os.getenv('ENVIRONMENT', 'development')}")

***REMOVED*** Import and create app using core module
from bff_api.core.app import create_app

***REMOVED*** Create default app instance
app = create_app()

if __name__ == "__main__":
    import sys
    from bff_api.cli.main import main

    ***REMOVED*** Forward to the CLI and pass the exit code to sys.exit
    sys.exit(main())
