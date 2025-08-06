***REMOVED*** 🎯 Next Steps for Alloy Configuration

***REMOVED******REMOVED*** ✅ **Metrics (Prometheus) - COMPLETED**

Your metrics configuration is now set up with:

- **URL**: `https://prometheus-prod-37-prod-ap-southeast-1.grafana.net/api/prom/push`
- **Username**: `2603597`
- **Password**: `glc_eyJ...` (API key configured)

***REMOVED******REMOVED*** 📝 **Logs (Loki) - NEEDED**

You still need to get the Loki configuration for logs. Here's how:

***REMOVED******REMOVED******REMOVED*** **Step 1: Get Loki Configuration**

1. **Go to Grafana Cloud Console**
2. **Navigate to**: Your Stack → Connections → Data Sources
3. **Find "Loki"** data source
4. **Look for connection details** similar to what you got for Prometheus

You should see something like:

```
loki.write "logs_hosted_loki" {
   endpoint {
      url = "https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push"
      basic_auth {
         username = "2603597"  // Same as metrics usually
         password = "glc_eyJ..."  // Might be same or different API key
      }
   }
}
```

***REMOVED******REMOVED******REMOVED*** **Step 2: Update Your .env File**

Once you get the Loki details, update these lines in `.env`:

```bash
***REMOVED*** Replace these placeholder values:
GRAFANA_CLOUD_LOGS_URL=https://logs-prod-XX-XX-X.grafana.net/loki/api/v1/push
GRAFANA_CLOUD_LOGS_USERNAME=your-logs-username
GRAFANA_CLOUD_LOGS_PASSWORD=your-logs-api-key
```

***REMOVED******REMOVED*** 🚀 **Testing Your Current Setup**

Even with just metrics configured, you can test:

```bash
cd infra/monitoring/alloy

***REMOVED*** Test configuration
docker-compose -f docker-compose.alloy.yml config

***REMOVED*** Start Alloy
docker-compose -f docker-compose.alloy.yml up -d

***REMOVED*** Check logs for successful metrics connection
docker-compose -f docker-compose.alloy.yml logs grafana-alloy
```

Look for messages like:

- ✅ `"level=info msg="remote_write initialized"`
- ✅ `"Connected to Prometheus remote write endpoint"`
- ❌ `"authentication failed"` or `"connection refused"`

***REMOVED******REMOVED*** 📊 **Verify Metrics in Grafana**

1. **Go to your Grafana Cloud dashboard**
2. **Navigate to Explore**
3. **Select Prometheus data source**
4. **Try this query**: `up{job="backend_api"}`
5. **Should see**: Metrics from your NextWatch services

***REMOVED******REMOVED*** 🔍 **Common Issues**

***REMOVED******REMOVED******REMOVED*** **If Authentication Fails**

```bash
***REMOVED*** Test connection manually
curl -u "2603597:glc_eyJ..." \
  "https://prometheus-prod-37-prod-ap-southeast-1.grafana.net/api/prom/push" \
  -X POST \
  --data-raw "***REMOVED*** TYPE test_metric counter
test_metric 1"
```

***REMOVED******REMOVED******REMOVED*** **If No Metrics Appear**

- Check if your services are exposing `/metrics` endpoints
- Verify Docker networks are connected
- Check Alloy UI at `http://localhost:12345/alloy`

***REMOVED******REMOVED*** 🎯 **Expected Results**

With metrics configured, you should see in Grafana:

- **Service health**: `up` metrics for each service
- **HTTP requests**: Request counts and response times
- **System metrics**: CPU, memory usage
- **Custom metrics**: Cache warming performance, etc.

***REMOVED******REMOVED*** 📋 **Complete Configuration Checklist**

- [x] ✅ Prometheus/Metrics configured
- [ ] ⏳ Loki/Logs configuration needed
- [ ] ⏳ Test metrics ingestion
- [ ] ⏳ Set up Grafana dashboards
- [ ] ⏳ Configure alerts

---

**🎉 You're halfway there! Get the Loki config and you'll have full observability.**
