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

***REMOVED*** Install package
echo "Installing movie-storage package..."
poetry install

***REMOVED*** Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

***REMOVED*** Display database info
echo -e "\033[0;34mUsing database:\033[0m $(python -c "from movie_storage.config.app import Config; config = Config.get_instance(); print(config._mask_database_password(config.database_url))")"

***REMOVED*** Drop all tables
echo -e "\033[0;33m⏳ Dropping all tables...\033[0m"
python -m movie_storage.cli teardown --drop-all --confirm --verbose

***REMOVED*** Initialize database
echo -e "\033[0;33m⏳ Initializing database...\033[0m"
python -m movie_storage.cli init --create-tables --verbose

***REMOVED*** Run migrations
echo -e "\033[0;33m⏳ Running migrations...\033[0m"
python -m movie_storage.cli migrate --verbose

echo -e "\033[0;32m✅ Database reset complete!\033[0m" 