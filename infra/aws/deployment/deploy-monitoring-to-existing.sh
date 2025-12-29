***REMOVED***!/bin/bash

***REMOVED*** Deploy NextWatch Monitoring Stack to Existing AWS Infrastructure

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🚀 Deploying NextWatch Monitoring to Existing AWS Infrastructure${NC}"
echo "=================================================================="

***REMOVED*** Load environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Loaded environment variables${NC}"
else
    echo -e "${RED}❌ Environment variables not found. Run check-environment.sh first.${NC}"
    exit 1
fi

***REMOVED*** Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra"
MONITORING_ENV_FILE="$INFRA_DIR/.env.monitoring.prod"

echo "Project root: $PROJECT_ROOT"
echo "Target instance: $INSTANCE_ID ($PUBLIC_IP)"

***REMOVED*** Verify monitoring environment file exists
if [ ! -f "$MONITORING_ENV_FILE" ]; then
    echo -e "${RED}❌ Monitoring environment file not found: $MONITORING_ENV_FILE${NC}"
    echo "Creating from template..."
    cp "$INFRA_DIR/env/monitoring.prod.example" "$MONITORING_ENV_FILE"
    echo -e "${YELLOW}⚠️  Please edit $MONITORING_ENV_FILE with your production values${NC}"
    exit 1
fi

***REMOVED*** Check if SSH key is available
SSH_KEY_PATH=""
for key in ~/.ssh/*.pem ~/.ssh/id_rsa ~/.ssh/id_ed25519; do
    if [ -f "$key" ]; then
        SSH_KEY_PATH="$key"
        break
    fi
done

if [ -z "$SSH_KEY_PATH" ]; then
    ***REMOVED*** Check if we're in one-click mode (non-interactive)
    if [ "${ONE_CLICK_MODE:-}" = "true" ]; then
        ***REMOVED*** In one-click mode, try common AWS key locations
        for common_key in ~/.ssh/nextwatch*.pem ~/.ssh/*aws*.pem ~/.ssh/*.pem; do
            if [ -f "$common_key" ]; then
                SSH_KEY_PATH="$common_key"
                echo "One-click mode: Using SSH key: $SSH_KEY_PATH"
                break
            fi
        done

        if [ -z "$SSH_KEY_PATH" ]; then
            echo -e "${RED}❌ SSH key not found automatically in one-click mode.${NC}"
            echo "Looked for: ~/.ssh/nextwatch*.pem, ~/.ssh/*aws*.pem, ~/.ssh/*.pem"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  SSH key not found. Please specify the path:${NC}"
        read -p "SSH key path: " SSH_KEY_PATH
        if [ ! -f "$SSH_KEY_PATH" ]; then
            echo -e "${RED}❌ SSH key not found: $SSH_KEY_PATH${NC}"
            exit 1
        fi
    fi
fi

echo "Using SSH key: $SSH_KEY_PATH"

***REMOVED*** Detect the user for SSH connection based on instance
***REMOVED*** Try ubuntu first (common for NextWatch deployments), then ec2-user
SSH_USER="ubuntu"
echo "Testing SSH connection with ubuntu user..."
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "echo 'test'" 2>/dev/null; then
    echo "Ubuntu user failed, trying ec2-user..."
    SSH_USER="ec2-user"
    if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP "echo 'test'" 2>/dev/null; then
        echo -e "${RED}❌ Neither ubuntu nor ec2-user work. Please check SSH configuration.${NC}"
        exit 1
    fi
fi

echo "SSH user: $SSH_USER"

***REMOVED*** Test SSH connection
echo -e "${YELLOW}🔑 Testing SSH connection...${NC}"
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}❌ SSH connection failed. Please check:${NC}"
    echo "  1. SSH key path: $SSH_KEY_PATH"
    echo "  2. Security group allows SSH from your IP"
    echo "  3. Instance is running and accessible"
    exit 1
fi

echo -e "${GREEN}✅ SSH connection successful${NC}"

***REMOVED*** Create temporary directory for files
TEMP_DIR="/tmp/nextwatch-monitoring-$$"
mkdir -p "$TEMP_DIR"

***REMOVED*** Copy necessary files to temp directory
echo -e "${YELLOW}📁 Preparing deployment files...${NC}"
cp -r "$INFRA_DIR/monitoring" "$TEMP_DIR/"
cp "$INFRA_DIR/docker-compose.monitoring.yml" "$TEMP_DIR/docker-compose.monitoring.yml"

***REMOVED*** Use the single monitoring environment file
if [ -f "$MONITORING_ENV_FILE" ]; then
    cp "$MONITORING_ENV_FILE" "$TEMP_DIR/.env.monitoring.prod"
    echo "✅ Using monitoring environment file: $MONITORING_ENV_FILE"
else
    echo -e "${RED}❌ Monitoring environment file not found: $MONITORING_ENV_FILE${NC}"
    echo "Please ensure the file exists before running deployment."
    exit 1
fi

***REMOVED*** Use the unified Prometheus configuration (no need to generate AWS-specific config)
echo -e "${YELLOW}⚙️  Using unified Prometheus configuration...${NC}"

***REMOVED*** Use the standard monitoring Docker Compose file (no need for AWS-specific version)
echo -e "${YELLOW}🐳 Using standard monitoring Docker Compose configuration...${NC}"

***REMOVED*** Create deployment script for the remote instance
cat > "$TEMP_DIR/remote-deploy.sh" << 'EOF'
***REMOVED***!/bin/bash

set -e

echo "🚀 Starting NextWatch Monitoring Deployment on AWS Instance"

***REMOVED*** Create monitoring directory
sudo mkdir -p /opt/nextwatch-monitoring
cd /opt/nextwatch-monitoring

***REMOVED*** Stop any existing monitoring services
echo "🛑 Stopping existing monitoring services..."
(sudo docker-compose -f docker-compose.monitoring.yml down || sudo docker compose -f docker-compose.monitoring.yml down) 2>/dev/null || true
(sudo docker-compose -f docker-compose.aws.yml down || sudo docker compose -f docker-compose.aws.yml down) 2>/dev/null || true

***REMOVED*** Clean up old monitoring containers
echo "🧹 Cleaning up old containers..."
sudo docker container prune -f
sudo docker volume prune -f

***REMOVED*** Check if Docker is running
if ! sudo docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Starting Docker..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

***REMOVED*** Check if Docker Compose is installed
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ***REMOVED*** Also try the newer 'docker compose' plugin approach
    if ! sudo docker compose version >/dev/null 2>&1; then
        echo "Installing Docker Compose plugin..."
        sudo apt-get update
        sudo apt-get install -y docker-compose-plugin
    fi
fi

***REMOVED*** Pull latest images
echo "📥 Pulling monitoring images..."
(sudo docker-compose -f docker-compose.monitoring.yml pull || sudo docker compose -f docker-compose.monitoring.yml pull)

***REMOVED*** Start monitoring stack
echo "🐳 Starting monitoring services..."
(sudo docker-compose -f docker-compose.monitoring.yml up -d || sudo docker compose -f docker-compose.monitoring.yml up -d)

***REMOVED*** Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

***REMOVED*** Check service status
echo "🏥 Checking service health..."
for service in prometheus-prod grafana-prod alertmanager-prod node-exporter-prod loki-prod promtail-prod cadvisor-prod blackbox-exporter-prod tempo-prod; do
    if sudo docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
        sudo docker logs "$service" --tail 20 2>/dev/null || echo "  Container not found or no logs"
    fi
done

***REMOVED*** Configure tracing for NextWatch services
echo "🔍 Configuring OpenTelemetry tracing..."
cat > /opt/nextwatch-monitoring/.env.tracing << 'TRACING_EOF'
***REMOVED*** Enable OpenTelemetry tracing for all services
ENABLE_TRACING=true
TRACING_ENDPOINT=http://tempo:4317
TRACING_SAMPLE_RATE=0.1

***REMOVED*** Service-specific tracing configuration
BACKEND_API_ENABLE_TRACING=true
BFF_API_ENABLE_TRACING=true
AUTH_API_ENABLE_TRACING=true
SEARCH_API_ENABLE_TRACING=true
RECOMMENDATION_API_ENABLE_TRACING=true
ML_API_ENABLE_TRACING=true

***REMOVED*** Logging configuration for trace correlation
LOG_FORMAT=json
LOG_STRUCTURED=true
OTEL_PYTHON_LOG_CORRELATION=true
TRACING_EOF
echo "✅ Tracing configuration created"

***REMOVED*** Test Tempo health
echo "🔍 Testing Tempo endpoint..."
sleep 10  ***REMOVED*** Give Tempo time to start
if curl -sf "http://localhost:3200/ready" >/dev/null 2>&1; then
    echo "✅ Tempo is ready and responding"
else
    echo "⚠️  Tempo health check failed - service may still be starting"
fi

***REMOVED*** Display access information
echo ""
echo "🎉 Monitoring stack deployment complete!"
echo ""
echo "🌐 Access URLs:"
echo "  Prometheus: http://\$(curl -s ifconfig.me):9090"
echo "  Grafana: http://\$(curl -s ifconfig.me):3001 (admin/<GRAFANA_ADMIN_PASSWORD>)"
echo "  AlertManager: http://\$(curl -s ifconfig.me):9093"
echo "  Loki: http://\$(curl -s ifconfig.me):3100"
echo ""
echo "📊 Service Status:"
(sudo docker-compose -f docker-compose.monitoring.yml ps || sudo docker compose -f docker-compose.monitoring.yml ps)
EOF

chmod +x "$TEMP_DIR/remote-deploy.sh"

***REMOVED*** Transfer files to remote instance
echo -e "${YELLOW}📤 Transferring files to AWS instance...${NC}"
scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no -r "$TEMP_DIR"/* "$SSH_USER@$PUBLIC_IP:/tmp/"

***REMOVED*** Execute deployment on remote instance
echo -e "${YELLOW}🚀 Executing deployment on remote instance...${NC}"
ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" << 'REMOTE_SCRIPT'
***REMOVED*** Move files to the correct location
sudo mkdir -p /opt/nextwatch-monitoring
sudo cp -r /tmp/monitoring /opt/nextwatch-monitoring/
sudo cp /tmp/docker-compose.monitoring.yml /opt/nextwatch-monitoring/
sudo cp /tmp/.env.monitoring.prod /opt/nextwatch-monitoring/.env 2>/dev/null || echo "Note: Environment file not found, will use defaults"
sudo cp /tmp/remote-deploy.sh /opt/nextwatch-monitoring/
sudo chown -R ubuntu:ubuntu /opt/nextwatch-monitoring

***REMOVED*** Execute the deployment
cd /opt/nextwatch-monitoring
bash remote-deploy.sh
REMOTE_SCRIPT

***REMOVED*** Clean up temporary files
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 NextWatch Monitoring Stack Deployed Successfully!${NC}"
echo "=================================================================="
echo ""
echo "🌐 Access your monitoring stack:"
echo "  🔍 Prometheus: http://$PUBLIC_IP:9090"
echo "  📊 Grafana: http://$PUBLIC_IP:3001"
echo "  📢 AlertManager: http://$PUBLIC_IP:9093"
echo ""
echo "🔐 Credentials:"
echo "  Grafana: admin / (set via GRAFANA_ADMIN_PASSWORD)"
echo ""
echo "🎯 Next Steps:"
echo "  1. Access Grafana and import NextWatch dashboards"
echo "  2. Configure alert notification channels"
echo "  3. Set up SSL/TLS with Let's Encrypt (optional)"
echo "  4. Configure domain-based access via reverse proxy"
echo ""
echo "📋 Quick Health Check:"
echo "  ssh -i $SSH_KEY_PATH $SSH_USER@$PUBLIC_IP 'cd /opt/nextwatch-monitoring && sudo docker-compose -f docker-compose.monitoring.yml ps'"
