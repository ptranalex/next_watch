***REMOVED***!/bin/bash

echo "🧪 Testing BFF API on AWS..."
echo "================================"

echo "1. Health Check (with redirect):"
curl -L -s https://alexsandbox.me/api/health | jq . || echo "❌ Health check failed"

echo -e "\n2. Health Check (direct with trailing slash):"
curl -s https://alexsandbox.me/api/health/ | jq . || echo "❌ Health check with slash failed"

echo -e "\n3. Movies endpoint:"
curl -s "https://alexsandbox.me/api/movies?limit=3" | jq . || echo "❌ Movies endpoint failed"

echo -e "\n4. Response time test:"
curl -w "\nTime: %{time_total}s | Status: %{http_code}\n" -s -o /dev/null -L https://alexsandbox.me/api/health

echo -e "\n5. CORS test:"
curl -s -I -X OPTIONS https://alexsandbox.me/api/health/ \
  -H "Origin: http://localhost:3000" | grep -i "access-control" || echo "❌ CORS headers not found"

echo -e "\n✅ BFF API tests completed!" 