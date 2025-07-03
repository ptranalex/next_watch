***REMOVED***!/bin/bash

***REMOVED*** One-Click NextWatch Monitoring Deployment to Existing AWS Infrastructure

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🚀 NextWatch Monitoring - One-Click AWS Deployment${NC}"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. ✅ Check your AWS environment"
echo "  2. 🔓 Configure security groups"
echo "  3. 🐳 Deploy monitoring stack"
echo ""

***REMOVED*** Confirmation
read -p "Continue with automated deployment? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 1/3: Checking AWS Environment${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Step 1: Check Environment
if ! ./infra/aws/setup/check-environment.sh; then
    echo -e "${RED}❌ Environment check failed. Please resolve issues before continuing.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 2/3: Configuring Security Groups${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Step 2: Configure Security Groups
export ONE_CLICK_MODE=true
if ! ./infra/aws/setup/open-monitoring-ports.sh; then
    echo -e "${RED}❌ Security group configuration failed.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 3/4: Deploying Monitoring Stack${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Step 3: Deploy Monitoring
export ONE_CLICK_MODE=true
if ! ./infra/aws/deployment/deploy-monitoring-to-existing.sh; then
    echo -e "${RED}❌ Monitoring deployment failed.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Step 4/4: Configuring Log Sync${NC}"
echo -e "${YELLOW}========================================${NC}"

***REMOVED*** Step 4: Fix Docker socket permissions for log sync
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    
    echo "🔧 Configuring Docker socket permissions for Promtail..."
    ssh -i ~/.ssh/aws_next_watch_may_7.pem ubuntu@$PUBLIC_IP 'sudo chmod 666 /var/run/docker.sock'
    echo -e "${GREEN}✅ Docker socket permissions configured${NC}"
    
    echo "🔄 Restarting Promtail to apply changes..."
    ssh -i ~/.ssh/aws_next_watch_may_7.pem ubuntu@$PUBLIC_IP 'cd /opt/nextwatch-monitoring && sudo docker-compose -f docker-compose.monitoring.yml restart promtail'
    echo -e "${GREEN}✅ Promtail restarted${NC}"
fi

echo ""
echo -e "${GREEN}🎉 ONE-CLICK DEPLOYMENT SUCCESSFUL!${NC}"
echo "================================================================"
echo ""

***REMOVED*** Load the environment variables to show final results
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    
    echo "🌐 Your NextWatch Monitoring Stack is now live:"
    echo ""
    echo "  📊 Grafana Dashboard:   https://alexsandbox.me/grafana/"
    echo "  🔍 Prometheus Metrics:  http://$PUBLIC_IP:9090"
    echo "  📢 AlertManager:        http://$PUBLIC_IP:9093"
    echo "  📋 Loki Logs:           http://$PUBLIC_IP:3100"
    echo "  🔍 Tempo Tracing:       http://$PUBLIC_IP:3200"
    echo ""
    echo "🔐 Login Credentials:"
    echo "  Grafana: admin / NextWatch2024Admin"
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
    echo "  ssh -i ~/.ssh/aws_next_watch_may_7.pem ubuntu@$PUBLIC_IP"
    echo "  cd /opt/nextwatch-monitoring"
    echo "  sudo docker-compose -f docker-compose.monitoring.yml ps"
    echo ""
    echo -e "${GREEN}🎊 Happy Monitoring! Your NextWatch observability is now complete.${NC}"
fi 