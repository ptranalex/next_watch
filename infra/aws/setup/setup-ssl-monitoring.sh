***REMOVED***!/bin/bash

***REMOVED*** Set up SSL/TLS for NextWatch Monitoring Stack using Let's Encrypt

set -e

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🔒 Setting up SSL/TLS for NextWatch Monitoring${NC}"
echo "================================================="

***REMOVED*** Load environment variables
if [ -f /tmp/nextwatch-aws-env.sh ]; then
    source /tmp/nextwatch-aws-env.sh
    echo -e "${GREEN}✅ Loaded environment variables${NC}"
else
    echo -e "${RED}❌ Environment variables not found. Run check-environment.sh first.${NC}"
    exit 1
fi

***REMOVED*** Get domain configuration
echo -e "${YELLOW}🌐 Domain Configuration${NC}"
read -p "Enter your domain for monitoring (e.g., monitoring.alexsandbox.me): " MONITORING_DOMAIN
read -p "Enter your email for Let's Encrypt: " LETSENCRYPT_EMAIL

if [ -z "$MONITORING_DOMAIN" ] || [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo -e "${RED}❌ Domain and email are required${NC}"
    exit 1
fi

echo "Domain: $MONITORING_DOMAIN"
echo "Email: $LETSENCRYPT_EMAIL"

***REMOVED*** Check if SSH key is available
SSH_KEY_PATH=""
for key in ~/.ssh/*.pem ~/.ssh/id_rsa ~/.ssh/id_ed25519; do
    if [ -f "$key" ]; then
        SSH_KEY_PATH="$key"
        break
    fi
done

if [ -z "$SSH_KEY_PATH" ]; then
    echo -e "${YELLOW}⚠️  SSH key not found. Please specify the path:${NC}"
    read -p "SSH key path: " SSH_KEY_PATH
fi

***REMOVED*** SSH user detection
SSH_USER="ubuntu"
if [[ "$INSTANCE_TYPE" == *"ubuntu"* ]]; then
    SSH_USER="ubuntu"
fi

***REMOVED*** Create SSL setup script
TEMP_DIR="/tmp/nextwatch-ssl-$$"
mkdir -p "$TEMP_DIR"

cat > "$TEMP_DIR/setup-ssl.sh" << EOF
***REMOVED***!/bin/bash

set -e

echo "🔒 Setting up SSL/TLS on AWS instance"

***REMOVED*** Install necessary packages
if command -v yum >/dev/null 2>&1; then
    ***REMOVED*** Amazon Linux
    sudo yum update -y
    sudo yum install -y nginx certbot python3-certbot-nginx
elif command -v apt >/dev/null 2>&1; then
    ***REMOVED*** Ubuntu
    sudo apt update
    sudo apt install -y nginx certbot python3-certbot-nginx
fi

***REMOVED*** Stop nginx if running
sudo systemctl stop nginx 2>/dev/null || true

***REMOVED*** Generate SSL certificate
echo "📜 Generating SSL certificate for $MONITORING_DOMAIN..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email $LETSENCRYPT_EMAIL \
    --domains $MONITORING_DOMAIN

***REMOVED*** Create nginx configuration for monitoring
sudo tee /etc/nginx/sites-available/nextwatch-monitoring << 'NGINX_CONFIG'
***REMOVED*** NextWatch Monitoring SSL Configuration

***REMOVED*** Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $MONITORING_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

***REMOVED*** HTTPS Configuration
server {
    listen 443 ssl http2;
    server_name $MONITORING_DOMAIN;

    ***REMOVED*** SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$MONITORING_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$MONITORING_DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    ***REMOVED*** Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    ***REMOVED*** Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        ***REMOVED*** Authentication (optional)
        ***REMOVED*** auth_basic "Monitoring";
        ***REMOVED*** auth_basic_user_file /etc/nginx/.htpasswd;
    }

    ***REMOVED*** Grafana
    location / {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;

        ***REMOVED*** WebSocket support for Grafana
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    ***REMOVED*** AlertManager
    location /alertmanager/ {
        proxy_pass http://localhost:9093/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    ***REMOVED*** Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_CONFIG

***REMOVED*** Enable the site
if [ -d "/etc/nginx/sites-enabled" ]; then
    sudo ln -sf /etc/nginx/sites-available/nextwatch-monitoring /etc/nginx/sites-enabled/
else
    ***REMOVED*** Amazon Linux - copy to conf.d
    sudo cp /etc/nginx/sites-available/nextwatch-monitoring /etc/nginx/conf.d/nextwatch-monitoring.conf
fi

***REMOVED*** Test nginx configuration
sudo nginx -t

***REMOVED*** Start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx

***REMOVED*** Set up certificate renewal
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

***REMOVED*** Update Grafana configuration for domain access
cd /opt/nextwatch-monitoring

***REMOVED*** Update docker-compose to use domain
sudo tee docker-compose.ssl.yml << DOCKER_SSL
services:
  ***REMOVED*** Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: prometheus-prod
    restart: always
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
      - '--web.external-url=https://$MONITORING_DOMAIN/prometheus/'
      - '--web.route-prefix=/'
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/rules/:/etc/prometheus/rules/
      - prometheus-data:/prometheus
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  ***REMOVED*** Grafana - Visualization
  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana-prod
    restart: always
    ports:
      - "127.0.0.1:3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_ADMIN_PASSWORD:-NextWatch2024Admin}
      - GF_SECURITY_SECRET_KEY=\${GRAFANA_SECRET_KEY:-NextWatchMonitoringSecretKey2024}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
      - GF_SERVER_DOMAIN=$MONITORING_DOMAIN
      - GF_SERVER_ROOT_URL=https://$MONITORING_DOMAIN/
      - GF_SERVER_SERVE_FROM_SUB_PATH=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring
    depends_on:
      - prometheus
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

  ***REMOVED*** AlertManager - Alert routing
  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager-prod
    restart: always
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=https://$MONITORING_DOMAIN/alertmanager/'
      - '--web.route-prefix=/'
    ports:
      - "127.0.0.1:9093:9093"
    volumes:
      - ./monitoring/alertmanager/alertmanager.prod.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager-data:/alertmanager
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  ***REMOVED*** Node Exporter - Host metrics
  node-exporter:
    image: prom/node-exporter:v1.7.0
    container_name: node-exporter-prod
    restart: always
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)(\$\$|/)'
    ports:
      - "127.0.0.1:9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring
    pid: host
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

volumes:
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
  alertmanager-data:
    driver: local

networks:
  monitoring:
    driver: bridge
DOCKER_SSL

***REMOVED*** Restart monitoring stack with SSL configuration
echo "🔄 Restarting monitoring stack with SSL configuration..."
if sudo docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="sudo docker compose"
else
    DOCKER_COMPOSE_CMD="sudo docker-compose"
fi

$DOCKER_COMPOSE_CMD -f docker-compose.ssl.yml --env-file .env.monitoring.prod down
$DOCKER_COMPOSE_CMD -f docker-compose.ssl.yml --env-file .env.monitoring.prod up -d

***REMOVED*** Display final status
echo ""
echo "🎉 SSL/TLS setup complete!"
echo ""
echo "🌐 Secure Access URLs:"
echo "  Grafana: https://$MONITORING_DOMAIN/"
echo "  Prometheus: https://$MONITORING_DOMAIN/prometheus/"
echo "  AlertManager: https://$MONITORING_DOMAIN/alertmanager/"
echo ""
echo "🔐 Certificate Information:"
sudo certbot certificates

echo ""
echo "📋 Nginx Status:"
sudo systemctl status nginx --no-pager -l
EOF

chmod +x "$TEMP_DIR/setup-ssl.sh"

***REMOVED*** Transfer and execute SSL setup
echo -e "${YELLOW}📤 Transferring SSL setup script...${NC}"
scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$TEMP_DIR/setup-ssl.sh" "$SSH_USER@$PUBLIC_IP:/tmp/"

echo -e "${YELLOW}🔒 Setting up SSL/TLS on remote instance...${NC}"
ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SSH_USER@$PUBLIC_IP" "bash /tmp/setup-ssl.sh"

***REMOVED*** Clean up
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 SSL/TLS Setup Complete!${NC}"
echo "==============================================="
echo ""
echo "🌐 Your NextWatch monitoring is now accessible via HTTPS:"
echo "  🔍 Grafana: https://$MONITORING_DOMAIN/"
echo "  📊 Prometheus: https://$MONITORING_DOMAIN/prometheus/"
echo "  📢 AlertManager: https://$MONITORING_DOMAIN/alertmanager/"
echo ""
echo "🔐 Security Features:"
echo "  ✅ Let's Encrypt SSL certificate"
echo "  ✅ Automatic certificate renewal"
echo "  ✅ Security headers enabled"
echo "  ✅ HTTP to HTTPS redirect"
echo ""
echo "🎯 Next Steps:"
echo "  1. Update DNS records to point $MONITORING_DOMAIN to $PUBLIC_IP"
echo "  2. Test SSL certificate: https://www.ssllabs.com/ssltest/"
echo "  3. Set up basic authentication (optional)"
echo "  4. Configure alert notification channels"
