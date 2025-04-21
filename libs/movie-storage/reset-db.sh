***REMOVED***!/bin/bash

***REMOVED*** Exit on error
set -e

***REMOVED*** Print warning
echo -e "\033[0;31m⚠️  WARNING: This script will completely reset your database ⚠️\033[0m"
echo "This is intended for development use only."
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Operation cancelled."
    exit 1
fi

***REMOVED*** Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
fi

***REMOVED*** Drop all tables
echo "Dropping all tables..."
movie-db teardown --drop-all --confirm

***REMOVED*** Initialize database
echo "Initializing database..."
movie-db init --create-tables

***REMOVED*** Run migrations
echo "Running migrations..."
movie-db migrate

echo -e "\033[0;32m✅ Database reset complete!\033[0m" 