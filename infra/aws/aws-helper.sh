#!/bin/bash

# NextWatch AWS Helper - Interactive Menu for AWS Scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 NextWatch AWS Infrastructure Helper${NC}"
echo "=================================================="
echo ""
echo "Choose an action:"
echo ""

# Deployment options
echo -e "${GREEN}📦 DEPLOYMENT${NC}"
echo "  1) 🚀 One-Click Monitoring Deployment (Recommended)"
echo "  2) 🔧 Deploy Monitoring to Existing Infrastructure"
echo ""

# Setup options
echo -e "${YELLOW}⚙️  SETUP & CONFIGURATION${NC}"
echo "  3) 🔍 Check AWS Environment"
echo "  4) 🔓 Open Monitoring Ports"
echo "  5) 🔒 Setup SSL/TLS for Monitoring"
echo ""

# Monitoring options
echo -e "${CYAN}📊 MONITORING UTILITIES${NC}"
echo "  6) 📋 Add Loki Log Integration"
echo ""

# Troubleshooting options
echo -e "${RED}🔧 TROUBLESHOOTING${NC}"
echo "  7) 🛠️  Fix Grafana Subpath Issues"
echo ""

# Information options
echo -e "${BLUE}📚 INFORMATION${NC}"
echo "  8) 📖 View Documentation"
echo "  9) 🌐 Show Access URLs"
echo ""

echo "  0) ❌ Exit"
echo ""

read -p "Enter your choice [0-9]: " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Starting One-Click Monitoring Deployment...${NC}"
        ./deployment/deploy-monitoring-one-click.sh
        ;;
    2)
        echo -e "${GREEN}🔧 Deploying Monitoring to Existing Infrastructure...${NC}"
        ./deployment/deploy-monitoring-to-existing.sh
        ;;
    3)
        echo -e "${YELLOW}🔍 Checking AWS Environment...${NC}"
        ./setup/check-environment.sh
        ;;
    4)
        echo -e "${YELLOW}🔓 Opening Monitoring Ports...${NC}"
        ./setup/open-monitoring-ports.sh
        ;;
    5)
        echo -e "${YELLOW}🔒 Setting up SSL/TLS...${NC}"
        ./setup/setup-ssl-monitoring.sh
        ;;
    6)
        echo -e "${CYAN}📋 Adding Loki Log Integration...${NC}"
        ./monitoring/add-loki-integration.sh
        ;;
    7)
        echo -e "${RED}🛠️  Fixing Grafana Subpath Issues...${NC}"
        ./troubleshooting/fix-grafana-subpath.sh
        ;;
    8)
        echo -e "${BLUE}📖 Opening Documentation...${NC}"
        if command -v less >/dev/null 2>&1; then
            less README.md
        else
            cat README.md
        fi
        ;;
    9)
        echo -e "${BLUE}🌐 Access URLs${NC}"
        echo "=================================================="
        if [ -f /tmp/nextwatch-aws-env.sh ]; then
            source /tmp/nextwatch-aws-env.sh
            echo "  📊 Grafana:      http://$PUBLIC_IP:3001 (admin/<GRAFANA_ADMIN_PASSWORD>)"
            echo "  🔍 Prometheus:   http://$PUBLIC_IP:9090"
            echo "  📢 AlertManager: http://$PUBLIC_IP:9093"
            echo "  📋 Loki:        http://$PUBLIC_IP:3100"
        else
            echo "  📊 Grafana:      http://YOUR_IP:3001 (admin/<GRAFANA_ADMIN_PASSWORD>)"
            echo "  🔍 Prometheus:   http://YOUR_IP:9090"
            echo "  📢 AlertManager: http://YOUR_IP:9093"
            echo "  📋 Loki:        http://YOUR_IP:3100"
            echo ""
            echo "  💡 Run option 3 (Check AWS Environment) to get your actual IP"
        fi
        echo ""
        echo "  🔐 Grafana Credentials: admin / (set via GRAFANA_ADMIN_PASSWORD)"
        echo ""
        ;;
    0)
        echo -e "${NC}👋 Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Please select 0-9.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Operation completed!${NC}"
echo ""
echo "Run './aws-helper.sh' again to perform another action."
