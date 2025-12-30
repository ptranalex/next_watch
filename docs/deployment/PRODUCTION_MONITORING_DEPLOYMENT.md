# Production Monitoring Deployment Guide

This guide covers deploying the NextWatch monitoring stack to production, including Prometheus, Grafana, AlertManager, Loki, and all supporting services.

## 🚀 **Quick Start**

### **1. Prerequisites**

- Docker and Docker Compose installed
- PostgreSQL database for Grafana (optional)
- SSL certificates (optional but recommended)
- SMTP server for email alerts

### **2. Environment Setup**

```bash
# Navigate to infrastructure directory
cd infra

# Copy environment template
cp env/monitoring.prod.example .env.monitoring.prod

# Edit with your production values
nano .env.monitoring.prod
```

### **3. Deploy Monitoring Stack**

```bash
# Run automated deployment script
./scripts/monitoring/deploy-production.sh
```

## 📋 **Detailed Deployment Steps**

### **Step 1: Infrastructure Preparation**

#### **Server Requirements**

- **CPU**: Minimum 4 cores, recommended 8 cores
- **Memory**: Minimum 8GB RAM, recommended 16GB
- **Storage**: Minimum 100GB SSD, recommended 500GB+
- **Network**: Reliable internet connection with adequate bandwidth

#### **Port Requirements**

```bash
# Monitoring Stack Ports
9090    # Prometheus
3001    # Grafana (mapped to avoid conflict)
9093    # AlertManager
3100    # Loki
9100    # Node Exporter
8080    # cAdvisor
9080    # Promtail
```

### **Step 2: Environment Configuration**

#### **Critical Environment Variables**

```bash
# Production Domain
PRODUCTION_DOMAIN=your-domain.com

# Grafana Security
GRAFANA_ADMIN_PASSWORD=your-super-secure-password
GRAFANA_SECRET_KEY=$(openssl rand -base64 32)

# Database Configuration
GRAFANA_DB_NAME=grafana_prod
GRAFANA_DB_USER=grafana_user
GRAFANA_DB_PASSWORD=your-db-password

# Email/SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=monitoring@your-domain.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=monitoring@your-domain.com

# Alert Routing
ALERT_EMAIL_TO=alerts@your-domain.com
CRITICAL_ALERT_EMAIL=critical@your-domain.com
WARNING_ALERT_EMAIL=warnings@your-domain.com
BUSINESS_ALERT_EMAIL=business@your-domain.com
INFRA_ALERT_EMAIL=infrastructure@your-domain.com
```

#### **Optional Advanced Configuration**

```bash
# Performance Tuning
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_RETENTION_SIZE=50GB
PROMETHEUS_MEMORY_LIMIT=2G
GRAFANA_MEMORY_LIMIT=1G

# Security
MONITORING_USERNAME=monitoring
MONITORING_PASSWORD=secure-monitoring-password

# Backup Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=nextwatch-monitoring-backups
```

### **Step 3: SSL Certificate Setup (Optional)**

#### **Using Let's Encrypt**

```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d monitoring.your-domain.com

# Update environment variables
SSL_CERT_PATH=/etc/letsencrypt/live/monitoring.your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/monitoring.your-domain.com/privkey.pem
```

### **Step 4: Network Configuration**

#### **Reverse Proxy Setup (Nginx)**

```nginx
# /etc/nginx/sites-available/monitoring
server {
    listen 443 ssl http2;
    server_name monitoring.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/monitoring.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitoring.your-domain.com/privkey.pem;

    # Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # AlertManager
    location /alertmanager/ {
        proxy_pass http://localhost:9093/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Step 5: Deployment Execution**

#### **Manual Deployment**

```bash
# 1. Deploy monitoring stack
cd infra
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod up -d

# 2. Verify services
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

# 3. Check logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs
```

#### **Automated Deployment**

```bash
# Run deployment script
chmod +x scripts/monitoring/deploy-production.sh
./scripts/monitoring/deploy-production.sh
```

## 🔧 **Post-Deployment Configuration**

### **Step 1: Grafana Setup**

1. Access Grafana: `https://your-domain.com/grafana/`
2. Login with admin credentials
3. Configure Prometheus data source:
   - URL: `http://prometheus:9090`
   - Access: `Server (default)`
4. Import dashboard templates
5. Configure alert channels

### **Step 2: Prometheus Configuration Validation**

1. Access Prometheus: `https://your-domain.com/prometheus/`
2. Check targets: Status → Targets
3. Verify all services are "UP"
4. Test queries:
   ```promql
   up
   http_requests_total
   bff_service_calls_total
   ```

### **Step 3: AlertManager Testing**

1. Access AlertManager: `https://your-domain.com/alertmanager/`
2. Check configuration
3. Test alert routing:
   ```bash
   # Trigger test alert
   curl -XPOST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[
     {
       "labels": {
         "alertname": "TestAlert",
         "severity": "warning"
       },
       "annotations": {
         "summary": "Test alert for monitoring setup"
       }
     }
   ]'
   ```

## 📊 **Monitoring and Maintenance**

### **Health Checks**

```bash
# Check service status
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

# Monitor resource usage
docker stats

# Check disk usage
df -h /var/lib/docker/volumes/
```

### **Backup Strategy**

```bash
# Run automated backup
./scripts/monitoring/backup-monitoring.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/scripts/monitoring/backup-monitoring.sh
```

### **Log Rotation**

```bash
# Configure Docker logging limits
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "5"
  }
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Services Not Starting**

```bash
# Check logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs [service-name]

# Check resources
docker system df
free -h

# Restart services
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod restart
```

#### **Permission Issues**

```bash
# Fix Grafana permissions
sudo chown -R 472:472 infra/monitoring/grafana/data

# Fix Prometheus permissions
sudo chown -R 65534:65534 infra/monitoring/prometheus/data
```

#### **Network Connectivity**

```bash
# Test internal networking
docker exec prometheus-prod ping grafana-prod

# Check exposed ports
netstat -tulpn | grep -E '(9090|3001|9093)'
```

### **Performance Optimization**

#### **Prometheus Tuning**

```yaml
# prometheus.prod.yml
global:
  scrape_interval: 15s # Balance between accuracy and load
  evaluation_interval: 15s # Alert evaluation frequency

# Retention settings
storage:
  tsdb:
    retention.time: 30d
    retention.size: 50GB
```

#### **Grafana Optimization**

```bash
# Database connection pooling
GF_DATABASE_MAX_OPEN_CONN=25
GF_DATABASE_MAX_IDLE_CONN=25
GF_DATABASE_CONN_MAX_LIFETIME=14400
```

## 🔐 **Security Considerations**

### **Access Control**

- Use strong passwords for all accounts
- Enable two-factor authentication where possible
- Restrict network access to monitoring ports
- Use SSL/TLS for all external communications

### **Data Protection**

- Encrypt data at rest
- Use secure communication channels
- Regular security updates
- Audit access logs

### **Firewall Configuration**

```bash
# UFW rules
sudo ufw allow from trusted-network to any port 9090  # Prometheus
sudo ufw allow from trusted-network to any port 3001  # Grafana
sudo ufw allow from trusted-network to any port 9093  # AlertManager
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**

- Deploy multiple Prometheus instances for high availability
- Use Prometheus federation for large deployments
- Scale Grafana with load balancers
- Implement AlertManager clustering

### **Vertical Scaling**

- Increase memory for Prometheus (data retention)
- Add CPU cores for query performance
- Expand storage for long-term retention
- Optimize queries and retention policies

## 📞 **Support and Maintenance**

### **Regular Tasks**

- [ ] Weekly: Review alert accuracy and thresholds
- [ ] Monthly: Update Docker images and configurations
- [ ] Quarterly: Review retention policies and storage usage
- [ ] Annually: Security audit and password rotation

### **Emergency Contacts**

- Infrastructure team: infrastructure@your-domain.com
- On-call rotation: oncall@your-domain.com
- Business stakeholders: business@your-domain.com

---

## 🎯 **Quick Reference**

### **Service URLs**

```
Prometheus:    https://your-domain.com/prometheus/
Grafana:       https://your-domain.com/grafana/
AlertManager:  https://your-domain.com/alertmanager/
Loki:          http://your-domain.com:3100
```

### **Key Commands**

```bash
# Deploy
./scripts/monitoring/deploy-production.sh

# Status
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

# Logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs -f

# Restart
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod restart

# Backup
./scripts/monitoring/backup-monitoring.sh
```

### **Important Files**

```
infra/compose/monitoring.yml             # Main deployment file
infra/.env.monitoring.prod                # Environment configuration
infra/monitoring/prometheus/              # Prometheus configs
infra/monitoring/grafana/                 # Grafana configs
infra/monitoring/alertmanager/            # AlertManager configs
```
