***REMOVED***!/bin/bash

***REMOVED*** Exit on error
set -e

***REMOVED*** Default action is upgrade
ACTION="upgrade"

***REMOVED*** Parse arguments
while [[ $***REMOVED*** -gt 0 ]]; do
  case $1 in
    --downgrade)
      ACTION="downgrade"
      shift
      ;;
    --help)
      echo "Usage: $0 [--downgrade] [--help]"
      echo ""
      echo "Options:"
      echo "  --downgrade    Downgrade the database to the previous version"
      echo "  --help         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

***REMOVED*** Install package in development mode
echo "Installing movie-storage package..."
poetry install

***REMOVED*** Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

if [ "$ACTION" == "downgrade" ]; then
  ***REMOVED*** Downgrade the database
  echo "Downgrading database to previous version..."
  python -m movie_storage.cli downgrade --confirm --verbose
  
  echo "Downgrade completed!"
else
  ***REMOVED*** Run database migration using the CLI
  echo "Running database migration..."
  python -m movie_storage.cli migrate --verbose
  
  echo "Migration completed!"
fi 