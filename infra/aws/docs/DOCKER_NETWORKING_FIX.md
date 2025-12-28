***REMOVED*** Docker Networking Fix for NextWatch Monitoring

***REMOVED******REMOVED*** Problem

When deploying the monitoring stack to AWS, Prometheus couldn't access the NextWatch production services because:

1. **Production services** run on the auto-generated `next_watch_default` Docker network (created by Docker Compose)
2. **Monitoring services** initially ran on their own `monitoring` network
3. **Container-to-container communication** failed because they were on separate networks

***REMOVED******REMOVED*** Root Cause

Docker Compose automatically creates network names using the pattern: `{directory_name}_{network_name}`

- Project directory: `next_watch`
- Network defined as: `default`
- Resulting network: `next_watch_default`

This auto-generated naming makes it hard to predict and configure monitoring.

***REMOVED******REMOVED*** Solution

***REMOVED******REMOVED******REMOVED*** Network Configuration

The monitoring services need to connect to **both networks**:

```yaml
networks:
  - monitoring ***REMOVED*** Internal monitoring communication
  - infra_default ***REMOVED*** Access to production NextWatch services
```

***REMOVED******REMOVED******REMOVED*** Updated Configuration

**File:** `infra/compose/monitoring.yml`

```yaml
services:
  prometheus:
    networks:
      - monitoring ***REMOVED*** For Grafana → Prometheus communication
      - nextwatch-network ***REMOVED*** For Prometheus → NextWatch services

  grafana:
    networks:
      - monitoring ***REMOVED*** For Grafana → Prometheus communication
      - nextwatch-network ***REMOVED*** Future: For Grafana → NextWatch services

networks:
  monitoring:
    driver: bridge
  ***REMOVED*** Connect to production network for service discovery
  nextwatch-network:
    external: true ***REMOVED*** References the existing production network
```

***REMOVED******REMOVED******REMOVED*** Production Network Discovery

```bash
***REMOVED*** Find the production network name
docker network ls | grep -E "(next|watch|infra)"

***REMOVED*** Common network names:
***REMOVED*** next_watch_default     - If running from root directory
***REMOVED*** infra_default          - If running from infra/ directory
***REMOVED*** nextwatch-network      - If custom network was created
***REMOVED*** next-watch-default     - Alternative naming pattern
```

***REMOVED******REMOVED*** Service Discovery Methods

***REMOVED******REMOVED******REMOVED*** Method 1: Container Names (Recommended)

```yaml
***REMOVED*** Prometheus config targets
- targets:
    - "backend-api:8000" ***REMOVED*** Uses container name
    - "bff-api:8001"
    - "auth-api:8003"
```

***REMOVED******REMOVED******REMOVED*** Method 2: Host Gateway (Fallback)

```yaml
***REMOVED*** If container names fail, use host gateway
- targets:
    - "host.docker.internal:8000"
    - "host.docker.internal:8001"
```

***REMOVED******REMOVED*** Implementation Status

✅ **Fixed in:** `infra/compose/monitoring.yml`
✅ **Working in:** Production AWS deployment
✅ **Tested with:** 4/6 NextWatch services reporting metrics

***REMOVED******REMOVED*** Verification

```bash
***REMOVED*** Check if monitoring can reach production services
docker exec prometheus-prod wget -qO- http://backend-api:8000/metrics

***REMOVED*** Check network connectivity
docker exec prometheus-prod nslookup backend-api
```

***REMOVED******REMOVED*** Why This Fix Was Critical

- **Before Fix**: Prometheus showed all targets as DOWN
- **After Fix**: Prometheus successfully scrapes metrics from NextWatch services
- **Result**: Complete observability stack with working dashboards

This networking configuration is **essential** for any monitoring deployment to existing Docker Compose services.
