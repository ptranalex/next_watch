***REMOVED***!/bin/bash
set -e

***REMOVED*** Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Installing local dependencies for backend-api..."

***REMOVED*** Install the local movie-storage package
echo "Installing movie-storage from $MONOREPO_ROOT/libs/movie-storage"
pip install -e "$MONOREPO_ROOT/libs/movie-storage"

echo "Local dependencies installed successfully!" 