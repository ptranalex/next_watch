***REMOVED***!/bin/bash

***REMOVED*** Add Loki Log Aggregation to NextWatch Monitoring Stack

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}📋 Adding Loki Log Aggregation to NextWatch Monitoring${NC}"
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

***REMOVED*** Deploy Loki integration
echo -e "${YELLOW}📋 Deploying Loki integration...${NC}"

ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" << 'REMOTE_SCRIPT'
cd /opt/nextwatch-monitoring

echo "🛑 Stopping monitoring services..."
sudo docker-compose -f docker-compose.aws.yml down

echo "📝 Updating Docker Compose with Loki services..."
***REMOVED*** Backup current configuration
sudo cp docker-compose.aws.yml docker-compose.aws.yml.backup

***REMOVED*** Add Loki and Promtail to existing configuration
sudo tee -a docker-compose.aws.yml << 'LOKI_CONFIG'

  ***REMOVED*** Loki - Log aggregation
  loki:
    image: grafana/loki:2.9.0
    container_name: loki-prod
    restart: always
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki/loki.prod.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    networks:
      - monitoring
    command: -config.file=/etc/loki/local-config.yaml
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3

  ***REMOVED*** Promtail - Log shipping to Loki
  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail-prod
    restart: always
    volumes:
      - ./monitoring/promtail/promtail.prod.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks:
      - monitoring
      - next_watch_default
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 256M
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
LOKI_CONFIG

***REMOVED*** Add Loki volume to volumes section
sudo sed -i '/^volumes:/a \  loki-data:\n    driver: local' docker-compose.aws.yml

echo "🐳 Starting monitoring stack with Loki..."
sudo docker-compose -f docker-compose.aws.yml --env-file .env.monitoring.prod up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🏥 Checking service health..."
sudo docker-compose -f docker-compose.aws.yml ps

echo ""
echo "🎉 Loki integration deployment complete!"
echo ""
echo "🌐 Access URLs:"
echo "  📋 Loki: http://$(curl -s ifconfig.me):3100"
echo "  📊 Grafana: http://$(curl -s ifconfig.me):3001 (now with Loki datasource)"
echo ""
echo "📝 Next Steps:"
echo "  1. Access Grafana and verify Loki datasource"
echo "  2. Create log dashboards" 
echo "  3. Set up log-based alerts"
REMOTE_SCRIPT

echo ""
echo -e "${GREEN}🎉 Loki Integration Added Successfully!${NC}"
echo "=================================================================="
echo ""
echo "🌐 Your monitoring now includes:"
echo "  📊 Metrics: Prometheus + Grafana"
echo "  📋 Logs: Loki + Promtail"
echo "  🖥️  System: Node Exporter"
echo ""
echo "🔍 Access Grafana: https://alexsandbox.me/grafana/"
echo "   - Prometheus datasource: Metrics"
echo "   - Loki datasource: Logs"
echo ""
echo "📋 Verify Loki is working:"
echo "  1. Go to Grafana → Explore"
echo "  2. Select 'Loki' datasource"
echo "  3. Query: {container_name=\"backend-api\"}" 