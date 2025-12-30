# 🔍 How to Get Loki Configuration from Grafana Cloud

## 🎯 **Quick Steps**

### **Method 1: Through Data Sources (Recommended)**

1. **Login to Grafana Cloud Console**

   - Go to `https://grafana.com/`
   - Login to your account
   - Select your stack (e.g., `yourstack.grafana.net`)

2. **Navigate to Data Sources**

   - In left sidebar: **Connections** → **Data sources**
   - OR go directly to: `https://yourstack.grafana.net/connections/datasources`

3. **Find Loki Data Source**

   - Look for **"Loki"** in the list
   - Click on it to open configuration

4. **Get Connection Details**
   - Look for **"URL"** field - copy this value
   - Look for authentication section with username/password
   - Should show something like:
     ```
     URL: https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push
     User: 2603597
     Password: glc_eyJ... (API key)
     ```

### **Method 2: Through Stack Settings**

1. **Go to Stack Overview**

   - From main Grafana Cloud dashboard
   - Click on your stack name

2. **Find "Send Logs" Section**

   - Look for **"Send logs"** or **"Loki"** configuration
   - Should show connection details

3. **Look for Alloy Configuration**
   - Some stacks show ready-made Alloy config blocks
   - Similar to the Prometheus config you got

### **Method 3: Through API Keys Page**

1. **Go to API Keys**

   - In your stack: **Administration** → **API Keys**
   - OR: `https://yourstack.grafana.net/org/apikeys`

2. **Create New API Key** (if needed)

   - Click **"Add API key"**
   - Name: `alloy-logs` or `nextwatch-logs`
   - Role: **Logs Publisher** or **Logs Writer**
   - Click **"Add"**

3. **Get the Details**
   - The URL pattern is usually: `https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push`
   - Username: Same as metrics (`2603597`)
   - Password: The new API key you generated

## 📋 **What You're Looking For**

You need these 3 values:

```bash
# Loki endpoint URL
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push

# Usually same as metrics username
GRAFANA_CLOUD_LOGS_USERNAME=2603597

# API key for logs (might be same as metrics or different)
GRAFANA_CLOUD_LOGS_PASSWORD=glc_eyJ...
```

## 🔍 **Visual Guide**

### **In Grafana Cloud Console:**

```
📊 Grafana Cloud Console
├── 🏠 Home
├── 📈 Dashboards
├── 🔌 Connections
│   ├── 📊 Data sources ← **Click here**
│   │   ├── ✅ Prometheus (already configured)
│   │   └── 📋 Loki ← **Click this one**
│   └── 🔌 Other connections
└── ⚙️ Administration
    └── 🔑 API Keys ← **Alternative: Create new key here**
```

### **In Loki Data Source Page:**

```
📋 Loki Data Source Configuration
├── 🔗 Connection
│   ├── URL: https://logs-prod-XX.grafana.net/loki/api/v1/push ← **Copy this**
│   └── Access: Server (default)
├── 🔐 Authentication
│   ├── Basic auth: ☑️ enabled
│   ├── User: 2603597 ← **Copy this**
│   └── Password: glc_eyJ... ← **Copy this**
└── 🧪 Test & Save
```

## 🚀 **Quick Test**

Once you have the values, test them:

```bash
# Test Loki connection
curl -u "2603597:YOUR_LOKI_API_KEY" \
  "https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "streams": [
      {
        "stream": {"job": "test"},
        "values": [["'$(date +%s%N)'", "test log message"]]
      }
    ]
  }'
```

Should return: `HTTP 204 No Content` (success)

## ❓ **If You Can't Find It**

### **Option A: Use Same Credentials**

Often the logs use the same credentials as metrics:

```bash
# Try using the same values as metrics
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-37-prod-ap-southeast-1.grafana.net/loki/api/v1/push
GRAFANA_CLOUD_LOGS_USERNAME=2603597
GRAFANA_CLOUD_LOGS_PASSWORD=glc_eyJ...
```

### **Option B: Check Stack Documentation**

- Look for **"Getting Started"** or **"Send Data"** guides
- Often has copy-paste configuration blocks

### **Option C: Contact Support**

- Grafana Cloud has good documentation
- Check: `https://grafana.com/docs/grafana-cloud/send-data/logs/`

## 🎯 **Expected Result**

You should get values like:

```bash
# Pattern for ap-southeast-1 region (same as your metrics)
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-37-prod-ap-southeast-1.grafana.net/loki/api/v1/push
GRAFANA_CLOUD_LOGS_USERNAME=2603597
GRAFANA_CLOUD_LOGS_PASSWORD=glc_eyJ... (same or different API key)
```

---

**🔍 Start with Method 1 (Data Sources) - it's the most reliable way to get the exact configuration!**
