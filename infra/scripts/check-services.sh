***REMOVED***!/bin/bash
echo '🔍 Checking Next Watch Services Status...'
echo

***REMOVED*** Check infrastructure services first
echo '🏗️ Infrastructure Services:'
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis (Homebrew) - UP (localhost:6379)"
else
    echo "❌ Redis (Homebrew) - DOWN"
fi

if docker ps | grep -q nextwatch-qdrant; then
    if curl -f -s http://localhost:6333/collections >/dev/null 2>&1; then
        echo "✅ Qdrant (Docker) - UP (localhost:6333)"
    else
        echo "⚠️  Qdrant container running but not responding"
    fi
else
    echo "❌ Qdrant (Docker) - DOWN"
fi

echo
echo '🚀 Application Services:'
services=(
    'Backend API:http://localhost:8000/health'
    'BFF API:http://localhost:8001/health' 
    'Recommendation API:http://localhost:8002/health'
    'Auth API:http://localhost:8003/health'
    'ML API:http://localhost:8004/health'
    'Search API:http://localhost:8005/health'
    'Frontend:http://localhost:3000'
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    url=$(echo $service | cut -d: -f2-)
    
    if curl -f -s $url > /dev/null 2>&1; then
        echo "✅ $name - UP"
    else
        echo "❌ $name - DOWN"
    fi
done

echo
echo '🐳 Docker Containers:'
docker ps --format "table {{.Names}}\t{{.Status}}" | grep nextwatch- || echo "No NextWatch containers running"
echo
echo '🍺 Homebrew Services:'
brew services list | grep redis || echo "Redis service status unknown"
