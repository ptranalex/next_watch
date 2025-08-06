***REMOVED***!/bin/bash

***REMOVED*** Grafana Alloy Docker Setup Script for NextWatch
***REMOVED*** This script sets up Grafana Alloy as a Docker container on AWS

set -e

echo "🚀 Setting up Grafana Alloy for NextWatch monitoring migration..."

***REMOVED*** Check if we're in the right directory
if [[ ! -f "docker-compose.alloy.yml" ]]; then
    echo "❌ Error: Please run this script from the infra/monitoring/alloy directory"
    exit 1
fi

***REMOVED*** Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and fill in your Grafana Cloud credentials:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

***REMOVED*** Validate environment variables
echo "🔍 Validating Grafana Cloud credentials..."
source .env

required_vars=(
    "GRAFANA_CLOUD_METRICS_URL"
    "GRAFANA_CLOUD_METRICS_USERNAME" 
    "GRAFANA_CLOUD_METRICS_PASSWORD"
    "GRAFANA_CLOUD_LOGS_URL"
    "GRAFANA_CLOUD_LOGS_USERNAME"
    "GRAFANA_CLOUD_LOGS_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

***REMOVED*** Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

***REMOVED*** Check if NextWatch networks exist
echo "🔍 Checking Docker networks..."
if ! docker network ls | grep -q "next_watch_default"; then
    echo "⚠️  Warning: next_watch_default network not found"
    echo "   Make sure NextWatch services are running first"
fi

if ! docker network ls | grep -q "monitoring"; then
    echo "📡 Creating monitoring network..."
    docker network create monitoring
fi

***REMOVED*** Pull the latest Alloy image
echo "📥 Pulling Grafana Alloy Docker image..."
docker pull grafana/alloy:latest

***REMOVED*** Stop existing Alloy container if running
echo "🛑 Stopping existing Alloy container..."
docker-compose -f docker-compose.alloy.yml down || true

***REMOVED*** Start Alloy
echo "🚀 Starting Grafana Alloy..."
docker-compose -f docker-compose.alloy.yml up -d

***REMOVED*** Wait for Alloy to start
echo "⏳ Waiting for Alloy to start..."
sleep 10

***REMOVED*** Check Alloy health
echo "🏥 Checking Alloy health..."
if curl -s http://localhost:12345/-/healthy >/dev/null; then
    echo "✅ Alloy is healthy and running!"
else
    echo "❌ Alloy health check failed"
    echo "📝 Check logs with: docker-compose -f docker-compose.alloy.yml logs grafana-alloy"
    exit 1
fi

***REMOVED*** Display useful information
echo ""
echo "🎉 Grafana Alloy setup complete!"
echo ""
echo "📊 Alloy UI: http://localhost:12345"
echo "📝 View logs: docker-compose -f docker-compose.alloy.yml logs -f grafana-alloy"
echo "🔄 Restart: docker-compose -f docker-compose.alloy.yml restart"
echo "🛑 Stop: docker-compose -f docker-compose.alloy.yml down"
echo ""
echo "📈 Next steps:"
echo "1. Visit http://localhost:12345 to see Alloy UI"
echo "2. Check Grafana Cloud for incoming metrics"
echo "3. Monitor metric series count to stay under 10k limit"
echo "4. Once stable, uncomment Tier 2 services in config.alloy"
echo ""
echo "⚠️  Free Tier Monitoring:"
echo "   - Expected series count: ~3,000-4,000 for Tier 1 services"
echo "   - Monitor usage at Grafana Cloud > Usage"
echo "   - Uncomment Tier 2 services only after validation"