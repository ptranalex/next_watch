# 🔐 Alloy Monitoring Credentials Setup

This guide shows you how to securely configure credentials for Grafana Cloud monitoring with Alloy.

## 🎯 **Required Credentials**

Your Alloy setup needs these Grafana Cloud credentials:

- **Metrics endpoint** (Prometheus/Mimir)
- **Logs endpoint** (Loki)
- **Traces endpoint** (Tempo) - optional

## 📋 **Step-by-Step Setup**

### **Step 1: Get Grafana Cloud Credentials**

1. **Login to [Grafana Cloud](https://grafana.com/)**
2. **Go to your stack** (e.g., `yourstack.grafana.net`)
3. **Navigate to Connections → Data Sources**

#### **For Metrics (Prometheus):**

- Find your **Prometheus/Mimir** data source
- Copy the **URL**: `https://prometheus-prod-XX-XX-X.grafana.net/api/prom/push`
- Copy **Username**: Usually your stack name or user ID
- Generate **API Key**: Settings → API Keys → Add API Key (MetricsPublisher role)

#### **For Logs (Loki):**

- Find your **Loki** data source
- Copy the **URL**: `https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push`
- Copy **Username**: Usually your stack name or user ID
- Generate **API Key**: Settings → API Keys → Add API Key (LogsPublisher role)

### **Step 2: Create Local Environment File**

```bash
cd infra/monitoring/alloy
cp .env.example .env
```

### **Step 3: Fill in Your Credentials**

Edit `.env` with your actual credentials:

```bash
# Grafana Cloud Configuration for NextWatch
# IMPORTANT: Keep this file secure and never commit to git!

# Grafana Cloud Metrics (Prometheus)
GRAFANA_CLOUD_METRICS_URL=https://prometheus-prod-13-prod-us-east-0.grafana.net/api/prom/push
GRAFANA_CLOUD_METRICS_USERNAME=123456
GRAFANA_CLOUD_METRICS_PASSWORD=glc_eyJ...

# Grafana Cloud Logs (Loki)
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-6.grafana.net/loki/api/v1/push
GRAFANA_CLOUD_LOGS_USERNAME=123456
GRAFANA_CLOUD_LOGS_PASSWORD=glc_eyJ...

# Optional: Grafana Cloud Traces (Tempo) - for future use
GRAFANA_CLOUD_TRACES_URL=https://tempo-prod-04-prod-us-east-0.grafana.net:443
GRAFANA_CLOUD_TRACES_USERNAME=123456
GRAFANA_CLOUD_TRACES_PASSWORD=glc_eyJ...
```

### **Step 4: Secure the Environment File**

```bash
# Make sure .env is not tracked by git
echo ".env" >> .gitignore

# Set proper permissions (owner read/write only)
chmod 600 .env

# Verify it's not in git
git status  # Should not show .env file
```

## 🚀 **Production Deployment Methods**

### **Method 1: Environment Variables (Recommended)**

For production servers, set environment variables directly:

```bash
# On your production server
export GRAFANA_CLOUD_METRICS_URL="https://prometheus-prod-XX-XX-X.grafana.net/api/prom/push"
export GRAFANA_CLOUD_METRICS_USERNAME="123456"
export GRAFANA_CLOUD_METRICS_PASSWORD="glc_eyJ..."
export GRAFANA_CLOUD_LOGS_URL="https://logs-prod-X.grafana.net/loki/api/v1/push"
export GRAFANA_CLOUD_LOGS_USERNAME="123456"
export GRAFANA_CLOUD_LOGS_PASSWORD="glc_eyJ..."

# Start Alloy
docker compose -f docker-compose.alloy.yml up -d
```

### **Method 2: Docker Secrets (Advanced)**

For high-security environments:

```yaml
# docker-compose.alloy.yml additions
services:
  grafana-alloy:
    # ... existing config ...
    secrets:
      - grafana_metrics_password
      - grafana_logs_password
    environment:
      - GRAFANA_CLOUD_METRICS_PASSWORD_FILE=/run/secrets/grafana_metrics_password
      - GRAFANA_CLOUD_LOGS_PASSWORD_FILE=/run/secrets/grafana_logs_password

secrets:
  grafana_metrics_password:
    file: ./secrets/grafana_metrics_password.txt
  grafana_logs_password:
    file: ./secrets/grafana_logs_password.txt
```

### **Method 3: CI/CD Secrets (GitHub Actions)**

Add to your deployment workflow:

```yaml
# In .github/workflows/deploy.yml
- name: Deploy Alloy Monitoring
  env:
    GRAFANA_CLOUD_METRICS_URL: ${{ secrets.GRAFANA_CLOUD_METRICS_URL }}
    GRAFANA_CLOUD_METRICS_USERNAME: ${{ secrets.GRAFANA_CLOUD_METRICS_USERNAME }}
    GRAFANA_CLOUD_METRICS_PASSWORD: ${{ secrets.GRAFANA_CLOUD_METRICS_PASSWORD }}
    GRAFANA_CLOUD_LOGS_URL: ${{ secrets.GRAFANA_CLOUD_LOGS_URL }}
    GRAFANA_CLOUD_LOGS_USERNAME: ${{ secrets.GRAFANA_CLOUD_LOGS_USERNAME }}
    GRAFANA_CLOUD_LOGS_PASSWORD: ${{ secrets.GRAFANA_CLOUD_LOGS_PASSWORD }}
  run: |
    cd infra/monitoring/alloy
    docker compose -f docker-compose.alloy.yml up -d
```

## 🔍 **Testing Your Configuration**

### **Test 1: Verify Environment Variables**

```bash
# Check if variables are loaded
docker compose -f docker-compose.alloy.yml config

# Should show resolved environment variables (passwords will be masked)
```

### **Test 2: Check Alloy Container Logs**

```bash
# Start Alloy and check logs
docker compose -f docker-compose.alloy.yml up -d
docker compose -f docker-compose.alloy.yml logs grafana-alloy

# Look for successful authentication messages
```

### **Test 3: Verify Metrics in Grafana**

1. Go to your Grafana Cloud dashboard
2. Navigate to **Explore**
3. Select **Prometheus** data source
4. Query: `up{job="backend_api"}`
5. Should see metrics from your services

### **Test 4: Verify Logs in Grafana**

1. In **Explore**, select **Loki** data source
2. Query: `{container_name="backend-api"}`
3. Should see log entries from your services

## 🚨 **Security Best Practices**

### **✅ DO:**

- Store credentials in environment variables or secrets management
- Use API keys with minimal required permissions
- Rotate API keys regularly (every 90 days)
- Monitor API key usage in Grafana Cloud
- Use different API keys for different environments

### **❌ DON'T:**

- Commit `.env` files to git
- Use admin-level API keys
- Share API keys between teams
- Hardcode credentials in config files
- Use the same credentials for dev/staging/prod

## 🔄 **Credential Rotation**

```bash
# 1. Generate new API keys in Grafana Cloud
# 2. Update environment variables
export GRAFANA_CLOUD_METRICS_PASSWORD="new_api_key_here"

# 3. Restart Alloy to pick up new credentials
docker compose -f docker-compose.alloy.yml restart grafana-alloy

# 4. Verify new credentials work
docker compose -f docker-compose.alloy.yml logs grafana-alloy

# 5. Revoke old API keys in Grafana Cloud
```

## 🆘 **Troubleshooting**

### **Common Issues:**

#### **Authentication Failed**

```bash
# Check if URLs and credentials are correct
curl -u "$GRAFANA_CLOUD_METRICS_USERNAME:$GRAFANA_CLOUD_METRICS_PASSWORD" \
  "$GRAFANA_CLOUD_METRICS_URL" \
  --data-raw "test metric"
```

#### **Environment Variables Not Loading**

```bash
# Verify .env file exists and has correct permissions
ls -la .env
cat .env  # Check content (be careful with sensitive data)

# Check if Docker Compose can read them
docker compose -f docker-compose.alloy.yml config | grep GRAFANA
```

#### **API Key Permissions**

- Make sure API keys have **MetricsPublisher** and **LogsPublisher** roles
- Check API key hasn't expired
- Verify you're using the correct stack endpoint URLs

---

## 📚 **Next Steps**

1. ✅ Set up credentials using this guide
2. ✅ Test local development environment
3. ✅ Deploy to production with environment variables
4. ✅ Monitor credential usage and rotate regularly
5. ✅ Set up alerts for authentication failures

**🔐 Remember: Treat these credentials like passwords - keep them secure!**
