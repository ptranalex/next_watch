***REMOVED***!/usr/bin/env bash
***REMOVED*** Helper script to stop NextWatch Docker containers
***REMOVED*** Note: Redis is managed by Homebrew and not stopped by this script

echo "🛑 Stopping NextWatch Docker containers..."

***REMOVED*** Stop Qdrant container only (Redis is Homebrew service)
docker stop nextwatch-qdrant 2>/dev/null || echo "No Qdrant container to stop"

***REMOVED*** Remove Qdrant container
docker rm nextwatch-qdrant 2>/dev/null || echo "No Qdrant container to remove"

echo "✅ NextWatch Docker containers stopped and removed"
echo "ℹ️  Redis (Homebrew service) is still running"
echo "   To stop Redis: brew services stop redis"
