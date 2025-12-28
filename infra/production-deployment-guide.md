***REMOVED*** 🚀 Next Watch Production Deployment with Full Observability

***REMOVED******REMOVED*** 📋 Prerequisites

1. **Server Setup**:

   - Docker 20.10+ installed
   - Docker Compose 2.0+ installed
   - PostgreSQL running on host (port 5432)
   - Redis running on host (port 6379)

2. **Required Files**:
   - All Docker images built and tagged
   - Environment files configured
   - Grafana Cloud credentials ready

***REMOVED******REMOVED*** 🔧 Step-by-Step Deployment

***REMOVED******REMOVED******REMOVED*** Step 1: Prepare Environment Files

```bash
cd /Users/alex/Sandbox/next_watch

***REMOVED*** Create production environment file
cp infra/env/prod.example .env.prod

***REMOVED*** (Optional) Add Grafana Cloud credentials for Alloy (metrics/logs/traces)
***REMOVED*** Copy values from: infra/monitoring/alloy/.env.example

***REMOVED*** Edit .env.prod with your actual values
nano .env.prod
```

**Required variables in `.env.prod`:**

```bash
***REMOVED*** Docker Images
DOCKER_BACKEND_IMAGE=next-watch-backend:latest
DOCKER_AUTH_IMAGE=next-watch-auth:latest
DOCKER_BFF_IMAGE=next-watch-bff:latest
DOCKER_FRONTEND_IMAGE=next-watch-frontend:latest
DOCKER_IMPORTER_IMAGE=next-watch-importer:latest
DOCKER_RECOMMENDATION_IMAGE=next-watch-recommendation:latest
DOCKER_SEARCH_IMAGE=next-watch-search:latest
DOCKER_ML_IMAGE=next-watch-ml:latest

***REMOVED*** Database
POSTGRES_USER=next_watch_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=next_watch

***REMOVED*** Security
JWT_SECRET=your-super-secure-jwt-secret-key
INTERNAL_API_KEY=your-internal-api-key

***REMOVED*** External APIs
TMDB_ACCESS_TOKEN=your-tmdb-token
OMDB_API_KEY=your-omdb-key

***REMOVED*** Observability (copy from infra/monitoring/alloy/.env.example)
GRAFANA_CLOUD_METRICS_URL=https://prometheus-prod-XX-XX-X.grafana.net/api/prom/push
GRAFANA_CLOUD_METRICS_USERNAME=your-metrics-username
GRAFANA_CLOUD_METRICS_PASSWORD=your-metrics-api-key
***REMOVED*** ... (logs + traces)
```

***REMOVED******REMOVED******REMOVED*** Step 2: Build Docker Images

```bash
***REMOVED*** Build all services in parallel
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest . &
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest . &
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest . &
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest . &
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest . &
docker build -f apps/recommendation-api/Dockerfile -t next-watch-recommendation:latest . &
docker build -f apps/search-api/Dockerfile -t next-watch-search:latest . &
docker build -f apps/ml-api/Dockerfile -t next-watch-ml:latest . &
wait

echo "✅ All Docker images built successfully"
```

***REMOVED******REMOVED******REMOVED*** Step 3: Deploy with Observability

```bash
***REMOVED*** Deploy the complete stack
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

***REMOVED*** Check deployment status
docker compose -f infra/compose/prod.yml ps
```

***REMOVED******REMOVED******REMOVED*** Step 4: Verify Deployment

```bash
***REMOVED*** Check service health
curl http://localhost:8000/health  ***REMOVED*** Backend API
curl http://localhost:8003/health  ***REMOVED*** Auth API
curl http://localhost:8001/health  ***REMOVED*** BFF API
curl http://localhost:3000/api/health  ***REMOVED*** Frontend

***REMOVED*** Check Grafana Alloy UI
curl http://localhost:12345/-/healthy

***REMOVED*** Check logs
docker compose -f infra/compose/prod.yml logs -f grafana-alloy
```

***REMOVED******REMOVED*** 🎯 What You Get

***REMOVED******REMOVED******REMOVED*** 📊 **Complete Observability Stack**

1. **Metrics** → Grafana Cloud Prometheus

   - Service health and performance metrics
   - Cache warming performance
   - Database query metrics

2. **Logs** → Grafana Cloud Loki

   - Centralized application logs
   - Error tracking and debugging
   - Cache warming operation logs

3. **Traces** → Grafana Cloud Tempo
   - Distributed tracing across all 8 microservices
   - Request flow visualization
   - Performance bottleneck identification

***REMOVED******REMOVED******REMOVED*** 🚀 **Production Services**

- **Frontend** (Next.js): Port 3000
- **BFF API**: Port 8001
- **Backend API**: Port 8000
- **Auth API**: Port 8003
- **Recommendation API**: Port 8002
- **Search API**: Port 8004
- **ML API**: Port 8005
- **Data Importer**: On-demand
- **Grafana Alloy**: Port 12345 (localhost only)

***REMOVED******REMOVED*** 🔍 Monitoring & Maintenance

***REMOVED******REMOVED******REMOVED*** View Real-Time Logs

```bash
***REMOVED*** All services
docker compose -f infra/compose/prod.yml logs -f

***REMOVED*** Specific service
docker compose -f infra/compose/prod.yml logs -f backend-api

***REMOVED*** Observability stack
docker compose -f infra/compose/prod.yml logs -f grafana-alloy
```

***REMOVED******REMOVED******REMOVED*** Service Management

```bash
***REMOVED*** Restart service
docker compose -f infra/compose/prod.yml restart backend-api

***REMOVED*** Update service
docker compose -f infra/compose/prod.yml up -d --no-deps backend-api

***REMOVED*** Scale service
docker compose -f infra/compose/prod.yml up -d --scale bff-api=2
```

***REMOVED******REMOVED******REMOVED*** Cache Warming Operations

```bash
***REMOVED*** Run cache warming via BFF API
docker exec -it bff-api python -m bff_api.cli warm-tier --tier popular --max-movies 100

***REMOVED*** Monitor warming progress in Grafana Cloud
***REMOVED*** → Logs: {service="bff-api"} |= "cache warming"
***REMOVED*** → Traces: Search for "cache_warming" operations
***REMOVED*** → Metrics: cache_warming_duration_seconds
```

***REMOVED******REMOVED*** 🎉 Success Indicators

**✅ Deployment Successful When:**

- All health checks pass
- Grafana Alloy shows "healthy" status
- Metrics appear in Grafana Cloud Prometheus
- Logs flow to Grafana Cloud Loki
- Traces appear in Grafana Cloud Tempo
- Frontend accessible at your domain
- Cache warming operations complete without errors

***REMOVED******REMOVED*** 🚨 Troubleshooting

**Service won't start:** Check logs and environment variables
**Observability not working:** Verify Grafana Cloud credentials
**Performance issues:** Monitor resource usage with `docker stats`
**Cache warming slow:** Check trace data for bottlenecks

---

**🎯 Your Next Watch platform now has production-grade observability!**
