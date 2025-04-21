***REMOVED***!/bin/bash

***REMOVED*** Exit on error
set -e

echo "Installing movie-storage package..."
poetry install

***REMOVED*** Activate virtual environment
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
else
  echo "No virtual environment found, using system Python"
fi

echo "Running database migration..."
python -m movie_storage.db.migrations

echo "Migration complete! You can also run migrations using:"
echo "  movie-db migrate" 