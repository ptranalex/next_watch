***REMOVED***!/bin/bash

***REMOVED*** Open monitoring ports in existing AWS security groups

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🔓 Opening NextWatch Monitoring Ports${NC}"
echo "=================================================="

***REMOVED*** Load environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Loaded environment variables${NC}"
else
    echo -e "${RED}❌ Environment variables not found. Run check-environment.sh first.${NC}"
    exit 1
fi

***REMOVED*** Get current public IP for secure access
echo -e "${YELLOW}🌐 Getting your current public IP...${NC}"
CURRENT_IP=$(curl -s ifconfig.me)
echo "Your current IP: $CURRENT_IP"

***REMOVED*** Open monitoring ports in security groups
for sg in $SECURITY_GROUPS; do
    echo -e "${YELLOW}🔒 Configuring security group: $sg${NC}"

    ***REMOVED*** Prometheus (9090) - restrict to current IP
    echo "Opening port 9090 (Prometheus) for $CURRENT_IP..."
    aws ec2 authorize-security-group-ingress \
        --group-id $sg \
        --protocol tcp \
        --port 9090 \
        --cidr "$CURRENT_IP/32" \
        --description "Prometheus monitoring access" 2>/dev/null || echo "  Port 9090 already open"

    ***REMOVED*** Grafana (3001) - restrict to current IP
    echo "Opening port 3001 (Grafana) for $CURRENT_IP..."
    aws ec2 authorize-security-group-ingress \
        --group-id $sg \
        --protocol tcp \
        --port 3001 \
        --cidr "$CURRENT_IP/32" \
        --description "Grafana dashboard access" 2>/dev/null || echo "  Port 3001 already open"

    ***REMOVED*** AlertManager (9093) - restrict to current IP
    echo "Opening port 9093 (AlertManager) for $CURRENT_IP..."
    aws ec2 authorize-security-group-ingress \
        --group-id $sg \
        --protocol tcp \
        --port 9093 \
        --cidr "$CURRENT_IP/32" \
        --description "AlertManager access" 2>/dev/null || echo "  Port 9093 already open"

    ***REMOVED*** Node Exporter (9100) - internal only
    echo "Opening port 9100 (Node Exporter) for internal access..."
    aws ec2 authorize-security-group-ingress \
        --group-id $sg \
        --protocol tcp \
        --port 9100 \
        --source-group $sg \
        --description "Node Exporter internal access" 2>/dev/null || echo "  Port 9100 already open"
done

***REMOVED*** Option to open ports for your domain (if using reverse proxy)
echo ""
echo -e "${YELLOW}🌐 Domain Access Configuration${NC}"

***REMOVED*** Check if we're in one-click mode (non-interactive)
if [ "${ONE_CLICK_MODE:-}" = "true" ]; then
    echo "One-click mode: Automatically configuring domain access for alexsandbox.me"
    domain_access="y"
else
    read -p "Do you want to open monitoring ports for domain access (alexsandbox.me)? [y/N]: " domain_access
fi

if [[ $domain_access =~ ^[Yy]$ ]]; then
    ***REMOVED*** Get domain IP
    DOMAIN_IP=$(dig +short alexsandbox.me | tail -n1)
    if [ -n "$DOMAIN_IP" ]; then
        echo "Domain IP: $DOMAIN_IP"

        for sg in $SECURITY_GROUPS; do
            ***REMOVED*** Open for domain IP
            aws ec2 authorize-security-group-ingress \
                --group-id $sg \
                --protocol tcp \
                --port 9090 \
                --cidr "$DOMAIN_IP/32" \
                --description "Prometheus domain access" 2>/dev/null || echo "  Domain access already configured"

            aws ec2 authorize-security-group-ingress \
                --group-id $sg \
                --protocol tcp \
                --port 3001 \
                --cidr "$DOMAIN_IP/32" \
                --description "Grafana domain access" 2>/dev/null || echo "  Domain access already configured"
        done
    fi
fi

***REMOVED*** Display current security group rules
echo ""
echo -e "${BLUE}📋 Current Security Group Rules:${NC}"
for sg in $SECURITY_GROUPS; do
    echo "Security Group: $sg"
    aws ec2 describe-security-groups \
        --group-ids $sg \
        --query "SecurityGroups[0].IpPermissions[?FromPort>=\`3000\` && FromPort<=\`9100\`].[FromPort,ToPort,IpRanges[0].CidrIp,IpRanges[0].Description]" \
        --output table
done

echo ""
echo -e "${GREEN}✅ Monitoring ports configuration complete!${NC}"
echo ""
echo "🔓 Opened ports:"
echo "  - 9090 (Prometheus) for $CURRENT_IP"
echo "  - 3001 (Grafana) for $CURRENT_IP"
echo "  - 9093 (AlertManager) for $CURRENT_IP"
echo "  - 9100 (Node Exporter) for internal access"
echo ""
echo "🚀 Next step: Run ./scripts/aws/deploy-monitoring-to-existing.sh"
