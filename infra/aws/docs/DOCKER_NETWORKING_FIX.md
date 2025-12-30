# Docker Networking Fix for NextWatch Monitoring

## Problem

When deploying the monitoring stack to AWS, Prometheus couldn't access the NextWatch production services because:

1. **Production services** run on the auto-generated `next_watch_default` Docker network (created by Docker Compose)
2. **Monitoring services** initially ran on their own `monitoring` network
3. **Container-to-container communication** failed because they were on separate networks

## Root Cause

Docker Compose automatically creates network names using the pattern: `{directory_name}_{network_name}`

- Project directory: `next_watch`
- Network defined as: `default`
- Resulting network: `next_watch_default`

This auto-generated naming makes it hard to predict and configure monitoring.

## Solution

### Network Configuration

The monitoring services need to connect to **both networks**:

```yaml
networks:
  - monitoring # Internal monitoring communication
  - infra_default # Access to production NextWatch services
```

### Updated Configuration

**File:** `infra/compose/monitoring.yml`

```yaml
services:
  prometheus:
    networks:
      - monitoring # For Grafana → Prometheus communication
      - nextwatch-network # For Prometheus → NextWatch services

  grafana:
    networks:
      - monitoring # For Grafana → Prometheus communication
      - nextwatch-network # Future: For Grafana → NextWatch services

networks:
  monitoring:
    driver: bridge
  # Connect to production network for service discovery
  nextwatch-network:
    external: true # References the existing production network
```

### Production Network Discovery

```bash
# Find the production network name
docker network ls | grep -E "(next|watch|infra)"

# Common network names:
# next_watch_default     - If running from root directory
# infra_default          - If running from infra/ directory
# nextwatch-network      - If custom network was created
# next-watch-default     - Alternative naming pattern
```

## Service Discovery Methods

### Method 1: Container Names (Recommended)

```yaml
# Prometheus config targets
- targets:
    - "backend-api:8000" # Uses container name
    - "bff-api:8001"
    - "auth-api:8003"
```

### Method 2: Host Gateway (Fallback)

```yaml
# If container names fail, use host gateway
- targets:
    - "host.docker.internal:8000"
    - "host.docker.internal:8001"
```

## Implementation Status

✅ **Fixed in:** `infra/compose/monitoring.yml`
✅ **Working in:** Production AWS deployment
✅ **Tested with:** 4/6 NextWatch services reporting metrics

## Verification

```bash
# Check if monitoring can reach production services
docker exec prometheus-prod wget -qO- http://backend-api:8000/metrics

# Check network connectivity
docker exec prometheus-prod nslookup backend-api
```

## Why This Fix Was Critical

- **Before Fix**: Prometheus showed all targets as DOWN
- **After Fix**: Prometheus successfully scrapes metrics from NextWatch services
- **Result**: Complete observability stack with working dashboards

This networking configuration is **essential** for any monitoring deployment to existing Docker Compose services.
