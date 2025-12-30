#!/bin/bash

# NextWatch Monitoring Log Sync Debugging Script
# This script helps diagnose log sync issues in the AWS-deployed monitoring stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 NextWatch Monitoring - Log Sync Debugging${NC}"
echo "========================================================"
echo ""

# Check if we have AWS environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Found AWS environment variables${NC}"
    echo "Public IP: $PUBLIC_IP"
else
    echo -e "${YELLOW}⚠️  AWS environment not found. Please provide connection details:${NC}"
    read -p "AWS Instance Public IP: " PUBLIC_IP
fi

# SSH key (do not hardcode local user paths in a public repo)
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
    echo -e "${YELLOW}⚠️  SSH key not found. Please specify the path:${NC}"
    read -p "SSH key path: " SSH_KEY_PATH
fi

echo ""
echo -e "${YELLOW}This script will SSH into your AWS instance and run diagnostics.${NC}"
read -p "Continue? [y/N]: " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Debugging cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Connecting to AWS instance...${NC}"

# Create the remote debugging script
cat << 'REMOTE_SCRIPT' > /tmp/aws-log-debug.sh
#!/bin/bash

# Colors for remote output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 NextWatch Log Sync Diagnostics${NC}"
echo "=================================="
echo ""

# Navigate to monitoring directory
cd /opt/nextwatch-monitoring || {
    echo -e "${RED}❌ Monitoring directory not found at /opt/nextwatch-monitoring${NC}"
    echo "Checking alternative locations..."
    find / -name "docker-compose.monitoring.yml" -type f 2>/dev/null | head -5
    exit 1
}

echo -e "${GREEN}✅ Found monitoring directory: $(pwd)${NC}"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}1. Docker Container Status${NC}"
echo -e "${YELLOW}========================================${NC}"
sudo docker-compose -f docker-compose.monitoring.yml ps
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}2. Promtail Container Logs (Last 50 lines)${NC}"
echo -e "${YELLOW}========================================${NC}"
sudo docker logs promtail-prod --tail 50
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}3. Loki Container Logs (Last 50 lines)${NC}"
echo -e "${YELLOW}========================================${NC}"
sudo docker logs loki-prod --tail 50
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}4. Volume Mounts and Permissions${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Checking log volumes:"
sudo docker volume ls | grep -E "(backend-logs|bff-logs|auth-logs|search-logs|recommendation-logs|ml-logs|frontend-logs)"
echo ""

echo "Checking volume mount points:"
sudo docker inspect promtail-prod | grep -A 20 '"Mounts"'
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}5. Log Files Accessibility${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Checking if Promtail can access log files:"
sudo docker exec promtail-prod ls -la /app/logs/ 2>/dev/null || echo "❌ Cannot access /app/logs/ in Promtail container"
sudo docker exec promtail-prod ls -la /var/lib/docker/containers/ 2>/dev/null | head -10 || echo "❌ Cannot access Docker container logs"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}6. Promtail Position File${NC}"
echo -e "${YELLOW}========================================${NC}"
sudo docker exec promtail-prod cat /tmp/positions.yaml 2>/dev/null || echo "❌ Cannot read positions file"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}7. Loki API Health Check${NC}"
echo -e "${YELLOW}========================================${NC}"
curl -s http://localhost:3100/ready || echo "❌ Loki not ready"
curl -s http://localhost:3100/metrics | grep promtail || echo "❌ No Promtail metrics in Loki"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}8. Network Connectivity${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Testing Promtail -> Loki connectivity:"
sudo docker exec promtail-prod wget -qO- http://loki:3100/ready 2>/dev/null || echo "❌ Promtail cannot reach Loki"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}9. Service Log Volumes on Host${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Checking NextWatch service log volumes:"
for service in backend bff auth search recommendation ml; do
    volume_path=$(sudo docker volume inspect ${service}-logs 2>/dev/null | grep '"Mountpoint"' | cut -d'"' -f4)
    if [ -n "$volume_path" ]; then
        echo "📁 ${service}-logs: $volume_path"
        sudo ls -la "$volume_path" 2>/dev/null | head -5 || echo "   ❌ Cannot access volume"
    else
        echo "❌ ${service}-logs volume not found"
    fi
done
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}10. Running Service Containers${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Checking if NextWatch services are running and generating logs:"
sudo docker ps | grep -E "(backend-api|bff-api|auth-api|search-api|recommendation-api|ml-api)"
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}11. Promtail Configuration${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Current Promtail config (first 30 lines):"
sudo docker exec promtail-prod cat /etc/promtail/config.yml | head -30
echo ""

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}12. Disk Space and Resources${NC}"
echo -e "${YELLOW}========================================${NC}"
df -h
echo ""
echo "Memory usage:"
free -h
echo ""

echo -e "${GREEN}🎯 Log Sync Diagnostic Summary${NC}"
echo "==============================="
echo ""
echo -e "${YELLOW}Common Issues to Check:${NC}"
echo "1. ❓ Are NextWatch services running and generating logs?"
echo "2. ❓ Are log volumes properly mounted in Promtail?"
echo "3. ❓ Can Promtail reach Loki over the network?"
echo "4. ❓ Are there permission issues accessing log files?"
echo "5. ❓ Is the 'next_watch_default' network properly configured?"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "• If services aren't running: Start them with:"
echo "  - sudo docker compose -f docker-compose.prod.yml up -d"
echo "  - (or) sudo docker-compose -f docker-compose.prod.yml up -d"
echo "• If volumes are missing: Restart monitoring stack to recreate volumes"
echo "• If network issues: Check docker network ls and inspect next_watch_default"
echo "• If permission issues: Fix volume ownership and restart Promtail"
echo ""

REMOTE_SCRIPT

# Copy script to remote server and execute
echo -e "${BLUE}📤 Uploading diagnostic script...${NC}"
scp -i "$SSH_KEY_PATH" /tmp/aws-log-debug.sh "$SSH_USER@$PUBLIC_IP:/tmp/"

echo -e "${BLUE}🔍 Running diagnostics on AWS instance...${NC}"
ssh -i "$SSH_KEY_PATH" "$SSH_USER@$PUBLIC_IP" 'chmod +x /tmp/aws-log-debug.sh && /tmp/aws-log-debug.sh'

echo ""
echo -e "${GREEN}🎉 Diagnostic Complete!${NC}"
echo ""
echo -e "${YELLOW}If you need to manually connect:${NC}"
echo "ssh -i $SSH_KEY_PATH $SSH_USER@$PUBLIC_IP"
echo ""
echo -e "${YELLOW}Common Fix Commands (run on AWS instance):${NC}"
echo ""
echo "# Restart just the logging components:"
echo "cd /opt/nextwatch-monitoring"
echo "sudo docker compose -f docker-compose.monitoring.yml restart promtail loki"
echo "  (or) sudo docker-compose -f docker-compose.monitoring.yml restart promtail loki"
echo ""
echo "# Restart entire monitoring stack:"
echo "sudo docker compose -f docker-compose.monitoring.yml down"
echo "sudo docker compose -f docker-compose.monitoring.yml up -d"
echo "  (or) sudo docker-compose -f docker-compose.monitoring.yml down"
echo "  (or) sudo docker-compose -f docker-compose.monitoring.yml up -d"
echo ""
echo "# Check if NextWatch services are running:"
echo "sudo docker compose -f docker-compose.prod.yml ps"
echo "  (or) sudo docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "# Start NextWatch services if needed:"
echo "sudo docker compose -f docker-compose.prod.yml up -d"
echo "  (or) sudo docker-compose -f docker-compose.prod.yml up -d"

# Clean up
rm -f /tmp/aws-log-debug.sh
