import logging
from pathlib import Path

***REMOVED*** Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

***REMOVED*** The CLI is now managed through the cli module
from data_importer.cli import app

if __name__ == "__main__":
    app()
