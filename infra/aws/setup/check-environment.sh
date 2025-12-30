#!/bin/bash

# NextWatch AWS Environment Check Script
# Verifies existing infrastructure before deploying monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 NextWatch AWS Environment Check${NC}"
echo "=================================================="

# Get current AWS identity
echo -e "${YELLOW}📋 AWS Identity:${NC}"
aws sts get-caller-identity --output table

# Get region
AWS_REGION=$(aws configure get region)
echo -e "${YELLOW}🌍 Current Region:${NC} $AWS_REGION"

# Check EC2 instances
echo -e "${YELLOW}🖥️  EC2 Instances:${NC}"
INSTANCES=$(aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*].[InstanceId,InstanceType,PublicIpAddress,PrivateIpAddress,Tags[?Key=='Name'].Value|[0]]" \
  --output table)

if [ -n "$INSTANCES" ]; then
    echo "$INSTANCES"

    # Get the main instance details
    MAIN_INSTANCE=$(aws ec2 describe-instances \
      --filters "Name=instance-state-name,Values=running" \
      --query "Reservations[0].Instances[0]" \
      --output json)

    if [ "$MAIN_INSTANCE" != "null" ]; then
        INSTANCE_ID=$(echo $MAIN_INSTANCE | jq -r '.InstanceId')
        PUBLIC_IP=$(echo $MAIN_INSTANCE | jq -r '.PublicIpAddress')
        PRIVATE_IP=$(echo $MAIN_INSTANCE | jq -r '.PrivateIpAddress')
        INSTANCE_TYPE=$(echo $MAIN_INSTANCE | jq -r '.InstanceType')
        VPC_ID=$(echo $MAIN_INSTANCE | jq -r '.VpcId')
        SUBNET_ID=$(echo $MAIN_INSTANCE | jq -r '.SubnetId')
        SECURITY_GROUPS=$(echo $MAIN_INSTANCE | jq -r '.SecurityGroups[].GroupId' | tr '\n' ' ')

        echo -e "${GREEN}✅ Main Instance Found:${NC}"
        echo "  Instance ID: $INSTANCE_ID"
        echo "  Type: $INSTANCE_TYPE"
        echo "  Public IP: $PUBLIC_IP"
        echo "  Private IP: $PRIVATE_IP"
        echo "  VPC: $VPC_ID"
        echo "  Subnet: $SUBNET_ID"
        echo "  Security Groups: $SECURITY_GROUPS"
    fi
else
    echo -e "${RED}❌ No running EC2 instances found${NC}"
    exit 1
fi

# Check security groups for monitoring ports
echo -e "${YELLOW}🔒 Security Group Analysis:${NC}"
for sg in $SECURITY_GROUPS; do
    echo "Checking security group: $sg"

    # Check if monitoring ports are open
    PROMETHEUS_OPEN=$(aws ec2 describe-security-groups \
      --group-ids $sg \
      --query "SecurityGroups[0].IpPermissions[?FromPort<=\`9090\` && ToPort>=\`9090\`]" \
      --output text)

    GRAFANA_OPEN=$(aws ec2 describe-security-groups \
      --group-ids $sg \
      --query "SecurityGroups[0].IpPermissions[?FromPort<=\`3001\` && ToPort>=\`3001\`]" \
      --output text)

    if [ -n "$PROMETHEUS_OPEN" ]; then
        echo -e "  ${GREEN}✅ Port 9090 (Prometheus) is accessible${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Port 9090 (Prometheus) needs to be opened${NC}"
    fi

    if [ -n "$GRAFANA_OPEN" ]; then
        echo -e "  ${GREEN}✅ Port 3001 (Grafana) is accessible${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Port 3001 (Grafana) needs to be opened${NC}"
    fi
done

# Check available disk space
echo -e "${YELLOW}💾 Storage Check:${NC}"
if [ -n "$PUBLIC_IP" ]; then
    echo "Note: SSH into $PUBLIC_IP to check disk space manually:"
    echo "  ssh -i ~/.ssh/your-key.pem ec2-user@$PUBLIC_IP 'df -h'"
fi

# Check if NextWatch services are running
echo -e "${YELLOW}🐳 NextWatch Services Check:${NC}"
echo "Note: Services are behind Nginx reverse proxy, checking via SSH..."

if [ -n "$PUBLIC_IP" ]; then
    # First try to check if SSH is accessible
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

    DOMAIN="${NEXTWATCH_DOMAIN:-${PRODUCTION_DOMAIN:-}}"

    if ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" "echo 'SSH test'" 2>/dev/null >/dev/null; then
        echo -e "${GREEN}✅ SSH connection available for service checks${NC}"

        # Check services via SSH (they're running on localhost inside the instance)
        ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" << 'REMOTE_CHECK'
echo "🐳 Checking NextWatch services via Docker..."
for port in 8000 8001 8002 8003 8004 8005; do
    SERVICE_NAME=""
    case $port in
        8000) SERVICE_NAME="Backend API" ;;
        8001) SERVICE_NAME="BFF API" ;;
        8002) SERVICE_NAME="Recommendation API" ;;
        8003) SERVICE_NAME="Auth API" ;;
        8004) SERVICE_NAME="ML API" ;;
        8005) SERVICE_NAME="Search API" ;;
    esac

    # Check if container is running
    if sudo docker ps --filter "publish=$port" --format "{{.Names}}" | grep -q .; then
        echo "  ✅ $SERVICE_NAME (port $port) container is running"

        # Check if health endpoint responds
        if curl -s --connect-timeout 3 http://localhost:$port/health > /dev/null 2>&1; then
            echo "    ✅ Health endpoint responding"
        else
            echo "    ⚠️  Health endpoint not responding (may not be implemented)"
        fi

        # Check if metrics endpoint exists
        if curl -s --connect-timeout 3 http://localhost:$port/metrics > /dev/null 2>&1; then
            echo "    ✅ Metrics endpoint available"
        else
            echo "    ⚠️  Metrics endpoint not accessible"
        fi
    else
        echo "  ❌ $SERVICE_NAME (port $port) container not found"
    fi
done

echo ""
echo "🌐 Checking domain access..."
if [ -n "$DOMAIN" ]; then
    if curl -s --connect-timeout 5 "https://$DOMAIN" > /dev/null; then
        echo "  ✅ $DOMAIN is accessible from server"
    else
        echo "  ⚠️  $DOMAIN not accessible from server"
    fi
else
    echo "  ⚠️  NEXTWATCH_DOMAIN not set; skipping domain check"
fi
REMOTE_CHECK
    else
        echo -e "${YELLOW}⚠️  SSH not accessible, checking domain instead...${NC}"

        # Check domain access as fallback
        if [ -n "$DOMAIN" ]; then
            if curl -s --connect-timeout 5 "https://$DOMAIN" > /dev/null; then
                echo -e "  ${GREEN}✅ NextWatch domain ($DOMAIN) is accessible${NC}"
                echo "  Note: Services are running behind Nginx reverse proxy"
            else
                echo -e "  ${RED}❌ NextWatch domain ($DOMAIN) is not accessible${NC}"
            fi
        else
            echo -e "  ${YELLOW}⚠️  NEXTWATCH_DOMAIN not set; skipping domain check${NC}"
        fi
    fi
fi

# Domain and SSL check
echo -e "${YELLOW}🌐 Domain & SSL Check:${NC}"
if [ -n "$DOMAIN" ] && curl -s --connect-timeout 5 "https://$DOMAIN" > /dev/null; then
    echo -e "  ${GREEN}✅ Domain $DOMAIN is accessible${NC}"

    # Check SSL certificate
    SSL_EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    echo "  SSL Certificate expires: $SSL_EXPIRY"
else
    if [ -n "$DOMAIN" ]; then
        echo -e "  ${YELLOW}⚠️  Domain $DOMAIN is not accessible${NC}"
    else
        echo -e "  ${YELLOW}⚠️  NEXTWATCH_DOMAIN not set; skipping SSL check${NC}"
    fi
fi

# Generate deployment summary
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo "=================================================="
echo "Target Instance: $INSTANCE_ID ($INSTANCE_TYPE)"
echo "Public IP: $PUBLIC_IP"
echo "VPC: $VPC_ID"
echo "Monitoring Ports Needed: 9090 (Prometheus), 3001 (Grafana), 9093 (AlertManager)"
echo ""
echo -e "${GREEN}✅ Environment check complete!${NC}"
echo ""
echo "🚀 Next steps:"
echo "1. Run: ./infra/aws/open-monitoring-ports.sh"
echo "2. Run: ./infra/aws/deploy-monitoring-to-existing.sh"

# Save environment info for next scripts
cat > /tmp/nextwatch-aws-env.sh << EOF
export AWS_REGION="$AWS_REGION"
export INSTANCE_ID="$INSTANCE_ID"
export PUBLIC_IP="$PUBLIC_IP"
export PRIVATE_IP="$PRIVATE_IP"
export VPC_ID="$VPC_ID"
export SUBNET_ID="$SUBNET_ID"
export SECURITY_GROUPS="$SECURITY_GROUPS"
EOF

echo "Environment variables saved to /tmp/nextwatch-aws-env.sh"
