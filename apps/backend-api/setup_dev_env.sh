***REMOVED***!/bin/bash
***REMOVED*** setup_dev_env.sh - Development environment setup script for Next Watch Backend API

***REMOVED*** Exit on error
set -e

echo "Setting up development environment for Next Watch Backend API"

***REMOVED*** Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
    echo "Please update .env with your PostgreSQL credentials if needed"
fi

***REMOVED*** Install dependencies
echo "Installing dependencies..."
poetry install

***REMOVED*** Initialize the database
echo "Setting up the database..."
poetry run python -m backend_api.scripts.setup_db setup-storage

echo "Development environment setup complete!"
echo "Run 'poetry run uvicorn backend_api.main:app --reload' to start the API server" 