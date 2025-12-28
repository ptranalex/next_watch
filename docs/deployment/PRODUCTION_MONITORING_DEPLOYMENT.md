***REMOVED*** Production Monitoring Deployment Guide

This guide covers deploying the NextWatch monitoring stack to production, including Prometheus, Grafana, AlertManager, Loki, and all supporting services.

***REMOVED******REMOVED*** 🚀 **Quick Start**

***REMOVED******REMOVED******REMOVED*** **1. Prerequisites**

- Docker and Docker Compose installed
- PostgreSQL database for Grafana (optional)
- SSL certificates (optional but recommended)
- SMTP server for email alerts

***REMOVED******REMOVED******REMOVED*** **2. Environment Setup**

```bash
***REMOVED*** Navigate to infrastructure directory
cd infra

***REMOVED*** Copy environment template
cp env/monitoring.prod.example .env.monitoring.prod

***REMOVED*** Edit with your production values
nano .env.monitoring.prod
```

***REMOVED******REMOVED******REMOVED*** **3. Deploy Monitoring Stack**

```bash
***REMOVED*** Run automated deployment script
./scripts/monitoring/deploy-production.sh
```

***REMOVED******REMOVED*** 📋 **Detailed Deployment Steps**

***REMOVED******REMOVED******REMOVED*** **Step 1: Infrastructure Preparation**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Server Requirements**

- **CPU**: Minimum 4 cores, recommended 8 cores
- **Memory**: Minimum 8GB RAM, recommended 16GB
- **Storage**: Minimum 100GB SSD, recommended 500GB+
- **Network**: Reliable internet connection with adequate bandwidth

***REMOVED******REMOVED******REMOVED******REMOVED*** **Port Requirements**

```bash
***REMOVED*** Monitoring Stack Ports
9090    ***REMOVED*** Prometheus
3001    ***REMOVED*** Grafana (mapped to avoid conflict)
9093    ***REMOVED*** AlertManager
3100    ***REMOVED*** Loki
9100    ***REMOVED*** Node Exporter
8080    ***REMOVED*** cAdvisor
9080    ***REMOVED*** Promtail
```

***REMOVED******REMOVED******REMOVED*** **Step 2: Environment Configuration**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Critical Environment Variables**

```bash
***REMOVED*** Production Domain
PRODUCTION_DOMAIN=your-domain.com

***REMOVED*** Grafana Security
GRAFANA_ADMIN_PASSWORD=your-super-secure-password
GRAFANA_SECRET_KEY=$(openssl rand -base64 32)

***REMOVED*** Database Configuration
GRAFANA_DB_NAME=grafana_prod
GRAFANA_DB_USER=grafana_user
GRAFANA_DB_PASSWORD=your-db-password

***REMOVED*** Email/SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=monitoring@your-domain.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=monitoring@your-domain.com

***REMOVED*** Alert Routing
ALERT_EMAIL_TO=alerts@your-domain.com
CRITICAL_ALERT_EMAIL=critical@your-domain.com
WARNING_ALERT_EMAIL=warnings@your-domain.com
BUSINESS_ALERT_EMAIL=business@your-domain.com
INFRA_ALERT_EMAIL=infrastructure@your-domain.com
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Optional Advanced Configuration**

```bash
***REMOVED*** Performance Tuning
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_RETENTION_SIZE=50GB
PROMETHEUS_MEMORY_LIMIT=2G
GRAFANA_MEMORY_LIMIT=1G

***REMOVED*** Security
MONITORING_USERNAME=monitoring
MONITORING_PASSWORD=secure-monitoring-password

***REMOVED*** Backup Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=nextwatch-monitoring-backups
```

***REMOVED******REMOVED******REMOVED*** **Step 3: SSL Certificate Setup (Optional)**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Using Let's Encrypt**

```bash
***REMOVED*** Install Certbot
sudo apt-get install certbot

***REMOVED*** Generate certificates
sudo certbot certonly --standalone -d monitoring.your-domain.com

***REMOVED*** Update environment variables
SSL_CERT_PATH=/etc/letsencrypt/live/monitoring.your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/monitoring.your-domain.com/privkey.pem
```

***REMOVED******REMOVED******REMOVED*** **Step 4: Network Configuration**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Reverse Proxy Setup (Nginx)**

```nginx
***REMOVED*** /etc/nginx/sites-available/monitoring
server {
    listen 443 ssl http2;
    server_name monitoring.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/monitoring.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitoring.your-domain.com/privkey.pem;

    ***REMOVED*** Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    ***REMOVED*** Grafana
    location /grafana/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    ***REMOVED*** AlertManager
    location /alertmanager/ {
        proxy_pass http://localhost:9093/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

***REMOVED******REMOVED******REMOVED*** **Step 5: Deployment Execution**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Manual Deployment**

```bash
***REMOVED*** 1. Deploy monitoring stack
cd infra
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod up -d

***REMOVED*** 2. Verify services
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

***REMOVED*** 3. Check logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Automated Deployment**

```bash
***REMOVED*** Run deployment script
chmod +x scripts/monitoring/deploy-production.sh
./scripts/monitoring/deploy-production.sh
```

***REMOVED******REMOVED*** 🔧 **Post-Deployment Configuration**

***REMOVED******REMOVED******REMOVED*** **Step 1: Grafana Setup**

1. Access Grafana: `https://your-domain.com/grafana/`
2. Login with admin credentials
3. Configure Prometheus data source:
   - URL: `http://prometheus:9090`
   - Access: `Server (default)`
4. Import dashboard templates
5. Configure alert channels

***REMOVED******REMOVED******REMOVED*** **Step 2: Prometheus Configuration Validation**

1. Access Prometheus: `https://your-domain.com/prometheus/`
2. Check targets: Status → Targets
3. Verify all services are "UP"
4. Test queries:
   ```promql
   up
   http_requests_total
   bff_service_calls_total
   ```

***REMOVED******REMOVED******REMOVED*** **Step 3: AlertManager Testing**

1. Access AlertManager: `https://your-domain.com/alertmanager/`
2. Check configuration
3. Test alert routing:
   ```bash
   ***REMOVED*** Trigger test alert
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

***REMOVED******REMOVED*** 📊 **Monitoring and Maintenance**

***REMOVED******REMOVED******REMOVED*** **Health Checks**

```bash
***REMOVED*** Check service status
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

***REMOVED*** Monitor resource usage
docker stats

***REMOVED*** Check disk usage
df -h /var/lib/docker/volumes/
```

***REMOVED******REMOVED******REMOVED*** **Backup Strategy**

```bash
***REMOVED*** Run automated backup
./scripts/monitoring/backup-monitoring.sh

***REMOVED*** Schedule daily backups
crontab -e
***REMOVED*** Add: 0 2 * * * /path/to/scripts/monitoring/backup-monitoring.sh
```

***REMOVED******REMOVED******REMOVED*** **Log Rotation**

```bash
***REMOVED*** Configure Docker logging limits
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "5"
  }
}
```

***REMOVED******REMOVED*** 🚨 **Troubleshooting**

***REMOVED******REMOVED******REMOVED*** **Common Issues**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Services Not Starting**

```bash
***REMOVED*** Check logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs [service-name]

***REMOVED*** Check resources
docker system df
free -h

***REMOVED*** Restart services
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod restart
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Permission Issues**

```bash
***REMOVED*** Fix Grafana permissions
sudo chown -R 472:472 infra/monitoring/grafana/data

***REMOVED*** Fix Prometheus permissions
sudo chown -R 65534:65534 infra/monitoring/prometheus/data
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Network Connectivity**

```bash
***REMOVED*** Test internal networking
docker exec prometheus-prod ping grafana-prod

***REMOVED*** Check exposed ports
netstat -tulpn | grep -E '(9090|3001|9093)'
```

***REMOVED******REMOVED******REMOVED*** **Performance Optimization**

***REMOVED******REMOVED******REMOVED******REMOVED*** **Prometheus Tuning**

```yaml
***REMOVED*** prometheus.prod.yml
global:
  scrape_interval: 15s ***REMOVED*** Balance between accuracy and load
  evaluation_interval: 15s ***REMOVED*** Alert evaluation frequency

***REMOVED*** Retention settings
storage:
  tsdb:
    retention.time: 30d
    retention.size: 50GB
```

***REMOVED******REMOVED******REMOVED******REMOVED*** **Grafana Optimization**

```bash
***REMOVED*** Database connection pooling
GF_DATABASE_MAX_OPEN_CONN=25
GF_DATABASE_MAX_IDLE_CONN=25
GF_DATABASE_CONN_MAX_LIFETIME=14400
```

***REMOVED******REMOVED*** 🔐 **Security Considerations**

***REMOVED******REMOVED******REMOVED*** **Access Control**

- Use strong passwords for all accounts
- Enable two-factor authentication where possible
- Restrict network access to monitoring ports
- Use SSL/TLS for all external communications

***REMOVED******REMOVED******REMOVED*** **Data Protection**

- Encrypt data at rest
- Use secure communication channels
- Regular security updates
- Audit access logs

***REMOVED******REMOVED******REMOVED*** **Firewall Configuration**

```bash
***REMOVED*** UFW rules
sudo ufw allow from trusted-network to any port 9090  ***REMOVED*** Prometheus
sudo ufw allow from trusted-network to any port 3001  ***REMOVED*** Grafana
sudo ufw allow from trusted-network to any port 9093  ***REMOVED*** AlertManager
```

***REMOVED******REMOVED*** 📈 **Scaling Considerations**

***REMOVED******REMOVED******REMOVED*** **Horizontal Scaling**

- Deploy multiple Prometheus instances for high availability
- Use Prometheus federation for large deployments
- Scale Grafana with load balancers
- Implement AlertManager clustering

***REMOVED******REMOVED******REMOVED*** **Vertical Scaling**

- Increase memory for Prometheus (data retention)
- Add CPU cores for query performance
- Expand storage for long-term retention
- Optimize queries and retention policies

***REMOVED******REMOVED*** 📞 **Support and Maintenance**

***REMOVED******REMOVED******REMOVED*** **Regular Tasks**

- [ ] Weekly: Review alert accuracy and thresholds
- [ ] Monthly: Update Docker images and configurations
- [ ] Quarterly: Review retention policies and storage usage
- [ ] Annually: Security audit and password rotation

***REMOVED******REMOVED******REMOVED*** **Emergency Contacts**

- Infrastructure team: infrastructure@your-domain.com
- On-call rotation: oncall@your-domain.com
- Business stakeholders: business@your-domain.com

---

***REMOVED******REMOVED*** 🎯 **Quick Reference**

***REMOVED******REMOVED******REMOVED*** **Service URLs**

```
Prometheus:    https://your-domain.com/prometheus/
Grafana:       https://your-domain.com/grafana/
AlertManager:  https://your-domain.com/alertmanager/
Loki:          http://your-domain.com:3100
```

***REMOVED******REMOVED******REMOVED*** **Key Commands**

```bash
***REMOVED*** Deploy
./scripts/monitoring/deploy-production.sh

***REMOVED*** Status
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod ps

***REMOVED*** Logs
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod logs -f

***REMOVED*** Restart
docker compose -f compose/monitoring.yml --env-file .env.monitoring.prod restart

***REMOVED*** Backup
./scripts/monitoring/backup-monitoring.sh
```

***REMOVED******REMOVED******REMOVED*** **Important Files**

```
infra/compose/monitoring.yml             ***REMOVED*** Main deployment file
infra/.env.monitoring.prod                ***REMOVED*** Environment configuration
infra/monitoring/prometheus/              ***REMOVED*** Prometheus configs
infra/monitoring/grafana/                 ***REMOVED*** Grafana configs
infra/monitoring/alertmanager/            ***REMOVED*** AlertManager configs
```
