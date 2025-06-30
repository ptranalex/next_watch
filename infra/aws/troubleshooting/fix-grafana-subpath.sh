***REMOVED***!/bin/bash

***REMOVED*** Fix Grafana Subpath Configuration for Nginx Reverse Proxy

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🔧 Fixing Grafana Subpath Configuration${NC}"
echo "=================================================================="

***REMOVED*** Load environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Loaded environment variables${NC}"
else
    echo -e "${RED}❌ Environment variables not found. Run check-environment.sh first.${NC}"
    exit 1
fi

***REMOVED*** Check SSH key
SSH_KEY_PATH="/Users/alex/.ssh/aws_next_watch_may_7.pem"
SSH_USER="ubuntu"

echo "Target instance: $INSTANCE_ID ($PUBLIC_IP)"
echo "Using SSH key: $SSH_KEY_PATH"

***REMOVED*** Test SSH connection
echo -e "${YELLOW}🔑 Testing SSH connection...${NC}"
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}❌ SSH connection failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SSH connection successful${NC}"

***REMOVED*** Fix Grafana configuration
echo -e "${YELLOW}🔧 Updating Grafana configuration for subpath serving...${NC}"

ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" << 'REMOTE_SCRIPT'
cd /opt/nextwatch-monitoring

echo "🛑 Stopping Grafana container..."
sudo docker stop grafana-prod || true
sudo docker rm grafana-prod || true

echo "🔧 Starting Grafana with subpath configuration..."
sudo docker run -d \
  --name grafana-prod \
  --restart always \
  -p 3001:3000 \
  --network nextwatch-monitoring_monitoring \
  --network next_watch_default \
  -e GF_SECURITY_ADMIN_PASSWORD=NextWatch2024Admin \
  -e GF_SECURITY_SECRET_KEY=NextWatchMonitoringSecretKey2024 \
  -e GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel \
  -e GF_SERVER_ROOT_URL=https://alexsandbox.me/grafana/ \
  -e GF_SERVER_SERVE_FROM_SUB_PATH=true \
  -v /opt/nextwatch-monitoring/monitoring/grafana/provisioning:/etc/grafana/provisioning \
  -v /opt/nextwatch-monitoring/monitoring/grafana/dashboards:/var/lib/grafana/dashboards \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:10.2.0

echo "⏳ Waiting for Grafana to start..."
sleep 15

echo "🏥 Checking Grafana health..."
if sudo docker ps --filter "name=grafana-prod" --filter "status=running" | grep -q "grafana-prod"; then
    echo "✅ Grafana is running with subpath configuration"
else
    echo "❌ Grafana failed to start"
    sudo docker logs grafana-prod --tail 20
fi

echo ""
echo "🎉 Grafana subpath configuration complete!"
echo ""
echo "🌐 Access URLs:"
echo "  📊 Grafana (via Nginx): https://alexsandbox.me/grafana/"
echo "  📊 Grafana (direct): http://$(curl -s ifconfig.me):3001"
echo ""
echo "🔐 Login: admin / NextWatch2024Admin"
REMOTE_SCRIPT

echo ""
echo -e "${GREEN}🎉 Grafana Subpath Fix Complete!${NC}"
echo "=================================================================="
echo ""
echo "🌐 Access Grafana:"
echo "  ✅ https://alexsandbox.me/grafana/ (should work now!)"
echo "  🔐 Login: admin / NextWatch2024Admin"
echo ""
echo "🔧 What was fixed:"
echo "  ✅ GF_SERVER_ROOT_URL=https://alexsandbox.me/grafana/"
echo "  ✅ GF_SERVER_SERVE_FROM_SUB_PATH=true"
echo ""
echo "📋 Test the fix:"
echo "  1. Go to https://alexsandbox.me/grafana/"
echo "  2. Should see Grafana login page (not redirect to /login)"
echo "  3. Login with admin / NextWatch2024Admin" 