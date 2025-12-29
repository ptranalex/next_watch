***REMOVED***!/bin/bash

***REMOVED*** NextWatch Monitoring Log Sync Verification Script
***REMOVED*** Quick check to verify logs are flowing from NextWatch services to Loki

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🔍 NextWatch Log Sync Verification${NC}"
echo "======================================"
echo ""

***REMOVED*** Check if we have AWS environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Found AWS environment variables${NC}"
    echo "Public IP: $PUBLIC_IP"
else
    echo -e "${YELLOW}⚠️  AWS environment not found. Please provide connection details:${NC}"
    read -p "AWS Instance Public IP: " PUBLIC_IP
fi

echo ""
echo -e "${BLUE}🔍 Running verification checks...${NC}"

***REMOVED*** SSH key (do not hardcode local user paths in a public repo)
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

***REMOVED*** Create the remote verification script
cat << 'REMOTE_VERIFY' > /tmp/aws-log-verify.sh
***REMOVED***!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Log Sync Verification${NC}"
echo "========================="
echo ""

cd /opt/nextwatch-monitoring || exit 1

if sudo docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="sudo docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="sudo docker-compose"
else
    echo -e "${RED}❌ Neither 'docker compose' nor 'docker-compose' found on host${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Checking monitoring containers status:${NC}"
$DOCKER_COMPOSE_CMD -f docker-compose.monitoring.yml ps | grep -E "(promtail|loki)"
echo ""

echo -e "${YELLOW}2. Testing Loki API:${NC}"
if curl -s http://localhost:3100/ready > /dev/null; then
    echo -e "${GREEN}✅ Loki is ready${NC}"
else
    echo -e "${RED}❌ Loki is not ready${NC}"
fi
echo ""

echo -e "${YELLOW}3. Checking available log labels:${NC}"
labels=$(curl -s http://localhost:3100/loki/api/v1/labels | jq -r '.data[]' 2>/dev/null | head -10)
if [ -n "$labels" ]; then
    echo -e "${GREEN}✅ Log labels found:${NC}"
    echo "$labels" | while read label; do
        echo "  - $label"
    done
else
    echo -e "${RED}❌ No log labels found${NC}"
fi
echo ""

echo -e "${YELLOW}4. Checking for NextWatch service logs:${NC}"
for service in backend bff auth search recommendation ml; do
    count=$(curl -s "http://localhost:3100/loki/api/v1/query_range?query={service=\"${service}-api\"}" | jq -r '.data.result | length' 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ]; then
        echo -e "${GREEN}✅ ${service}-api: $count log streams found${NC}"
    else
        echo -e "${YELLOW}⚠️  ${service}-api: No logs found (may take a few minutes)${NC}"
    fi
done
echo ""

echo -e "${YELLOW}5. Recent Promtail activity:${NC}"
sudo docker logs promtail-prod --tail 5 | head -5
echo ""

echo -e "${YELLOW}6. Checking volume mounts:${NC}"
volumes_ok=true
for vol in next_watch_backend-logs next_watch_bff-logs next_watch_auth-logs; do
    if sudo docker volume inspect $vol > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $vol exists${NC}"
    else
        echo -e "${RED}❌ $vol missing${NC}"
        volumes_ok=false
    fi
done

if $volumes_ok; then
    echo -e "${GREEN}✅ All required volumes are present${NC}"
else
    echo -e "${RED}❌ Some volumes are missing - check if NextWatch services are running${NC}"
fi
echo ""

echo -e "${BLUE}📊 Summary:${NC}"
echo "==============="
if curl -s http://localhost:3100/ready > /dev/null && [ -n "$labels" ]; then
    echo -e "${GREEN}🎉 Log sync is working! Check Grafana for logs.${NC}"
    echo ""
    echo -e "${YELLOW}Access your logs at:${NC}"
    echo "  📊 Grafana: https://${NEXTWATCH_DOMAIN:-your-domain.com}/grafana/"
    echo "  🔍 Go to Explore → Select Loki datasource"
    echo "  📋 Query examples:"
    echo "    {service=\"backend-api\"}"
    echo "    {service=\"bff-api\"} |= \"ERROR\""
    echo "    {service=\"auth-api\"} | json"
else
    echo -e "${YELLOW}⚠️  Log sync may still be starting up or needs attention.${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Wait 2-3 more minutes for services to initialize"
    echo "2. Check if NextWatch services are running:"
    echo "   sudo docker ps | grep -E \"(backend|bff|auth|search|recommendation|ml)\""
    echo "3. If issues persist, run the debug script:"
    echo "   ./infra/scripts/debug-aws-log-sync.sh"
fi

REMOTE_VERIFY

***REMOVED*** Copy script to remote server and execute
echo -e "${BLUE}📤 Uploading verification script...${NC}"
scp -i "$SSH_KEY_PATH" /tmp/aws-log-verify.sh "$SSH_USER@$PUBLIC_IP:/tmp/"

echo -e "${BLUE}🔍 Running verification on AWS instance...${NC}"
ssh -i "$SSH_KEY_PATH" "$SSH_USER@$PUBLIC_IP" 'chmod +x /tmp/aws-log-verify.sh && /tmp/aws-log-verify.sh'

echo ""
echo -e "${GREEN}🎉 Verification Complete!${NC}"

***REMOVED*** Clean up
rm -f /tmp/aws-log-verify.sh
