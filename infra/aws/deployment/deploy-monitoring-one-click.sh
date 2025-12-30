#!/bin/bash

# One-Click NextWatch Monitoring Deployment to Existing AWS Infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 NextWatch Monitoring - One-Click AWS Deployment${NC}"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. ✅ Check your AWS environment"
echo "  2. 🔓 Configure security groups"
echo "  3. 🐳 Deploy monitoring stack"
echo ""

# Confirmation
read -p "Continue with automated deployment? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 1/3: Checking AWS Environment${NC}"
echo -e "${YELLOW}========================================${NC}"

# Step 1: Check Environment
if ! ./infra/aws/setup/check-environment.sh; then
    echo -e "${RED}❌ Environment check failed. Please resolve issues before continuing.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 2/3: Configuring Security Groups${NC}"
echo -e "${YELLOW}========================================${NC}"

# Step 2: Configure Security Groups
export ONE_CLICK_MODE=true
if ! ./infra/aws/setup/open-monitoring-ports.sh; then
    echo -e "${RED}❌ Security group configuration failed.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 3/4: Deploying Monitoring Stack${NC}"
echo -e "${YELLOW}========================================${NC}"

# Step 3: Deploy Monitoring
export ONE_CLICK_MODE=true
if ! ./infra/aws/deployment/deploy-monitoring-to-existing.sh; then
    echo -e "${RED}❌ Monitoring deployment failed.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 4/4: Configuring Log Sync${NC}"
echo -e "${YELLOW}========================================${NC}"

# Step 4: Fix Docker socket permissions for log sync
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh

    SSH_USER="${SSH_USER:-ubuntu}"
    SSH_KEY_PATH="${SSH_KEY_PATH:-}"
    if [ -z "$SSH_KEY_PATH" ]; then
        for key in ~/.ssh/*.pem ~/.ssh/id_rsa ~/.ssh/id_ed25519; do
            if [ -f "$key" ]; then
                SSH_KEY_PATH="$key"
                break
            fi
        done
    fi

    if [ -z "$SSH_KEY_PATH" ]; then
        echo -e "${RED}❌ SSH key not found. Set SSH_KEY_PATH env var or ensure a key exists in ~/.ssh.${NC}"
        exit 1
    fi

    echo "🔧 Configuring Docker socket permissions for Promtail..."
    ssh -i "$SSH_KEY_PATH" "$SSH_USER@$PUBLIC_IP" 'sudo chmod 666 /var/run/docker.sock'
    echo -e "${GREEN}✅ Docker socket permissions configured${NC}"

    echo "🔄 Restarting Promtail to apply changes..."
    ssh -i "$SSH_KEY_PATH" "$SSH_USER@$PUBLIC_IP" 'cd /opt/nextwatch-monitoring && (sudo docker compose -f docker-compose.monitoring.yml restart promtail || sudo docker-compose -f docker-compose.monitoring.yml restart promtail)'
    echo -e "${GREEN}✅ Promtail restarted${NC}"
fi

echo ""
echo -e "${GREEN}🎉 ONE-CLICK DEPLOYMENT SUCCESSFUL!${NC}"
echo "================================================================"
echo ""

# Load the environment variables to show final results
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh

    echo "🌐 Your NextWatch Monitoring Stack is now live:"
    echo ""
    echo "  📊 Grafana Dashboard:   https://${NEXTWATCH_DOMAIN:-your-domain.com}/grafana/"
    echo "  🔍 Prometheus Metrics:  http://$PUBLIC_IP:9090"
    echo "  📢 AlertManager:        http://$PUBLIC_IP:9093"
    echo "  📋 Loki Logs:           http://$PUBLIC_IP:3100"
    echo "  🔍 Tempo Tracing:       http://$PUBLIC_IP:3200"
    echo ""
    echo "🔐 Login Credentials:"
    echo "  Grafana: admin / (set via GRAFANA_ADMIN_PASSWORD in your env file)"
    echo ""
    echo "🎯 What's Being Monitored:"
    echo "  📈 Metrics: Backend API, BFF API, Recommendation API, Auth API, ML API, Search API"
    echo "  📋 Logs: All NextWatch service logs via Docker containers"
    echo "  🔍 Traces: Distributed tracing across all services with Tempo"
    echo "  🖥️  System: CPU, Memory, Disk, Network (Node Exporter)"
    echo "  🔄 Real-time: Live log tailing, metrics streaming, and trace visualization"
    echo ""
    echo "🔧 Optional Next Steps:"
    echo "  • Set up SSL/TLS: ./setup-ssl-monitoring.sh"
    echo "  • Configure email alerts in Grafana"
    echo "  • Import custom dashboards"
    echo ""
    echo "📋 Troubleshooting:"
    echo "  ssh -i $SSH_KEY_PATH $SSH_USER@$PUBLIC_IP"
    echo "  cd /opt/nextwatch-monitoring"
    echo "  sudo docker compose -f docker-compose.monitoring.yml ps  (or: sudo docker-compose -f docker-compose.monitoring.yml ps)"
    echo ""
    echo -e "${GREEN}🎊 Happy Monitoring! Your NextWatch observability is now complete.${NC}"
fi
