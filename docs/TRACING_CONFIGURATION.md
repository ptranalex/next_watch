***REMOVED*** Tracing Configuration Guide

This document shows how to properly enable OpenTelemetry tracing in NextWatch using the **existing environment configuration system**.

***REMOVED******REMOVED*** 🎯 **No Separate .env.tracing Files Needed**

NextWatch already has a sophisticated environment management system. **Tracing configuration integrates seamlessly** with the existing `.env` file hierarchy.

***REMOVED******REMOVED*** 📁 **Environment File Hierarchy (Existing System)**

NextWatch uses this priority order:

```bash
1. Environment variables (highest priority)
2. .env.local (local development overrides)
3. .env.{environment} (e.g., .env.development, .env.production)
4. .env (base configuration)
5. Default values in code (lowest priority)
```

***REMOVED******REMOVED*** 🔧 **How to Enable Tracing**

***REMOVED******REMOVED******REMOVED*** **Method 1: Environment Variables (Recommended for Testing)**

```bash
***REMOVED*** Quick enable for development
export ENVIRONMENT=development
export ENABLE_TRACING=true
export TRACING_SAMPLE_RATE=1.0

***REMOVED*** Start any service - tracing automatically configured
cd apps/backend-api
hatch run python -m uvicorn backend_api.main:create_app --factory
```

***REMOVED******REMOVED******REMOVED*** **Method 2: Add to .env.local (Persistent Development)**

```bash
***REMOVED*** apps/backend-api/.env.local (or any service)
ENABLE_TRACING=true
TRACING_ENDPOINT=http://localhost:4317
TRACING_SAMPLE_RATE=1.0
SERVICE_NAME=backend-api
```

***REMOVED******REMOVED******REMOVED*** **Method 3: Environment-Specific Files (Production)**

Already configured in:

- `infra/.env.development` → 100% sampling
- `infra/.env.production` → 5% sampling

***REMOVED******REMOVED*** 📊 **Tracing Configuration Options**

***REMOVED******REMOVED******REMOVED*** **Core Settings**

| Variable              | Development             | Production          | Description             |
| --------------------- | ----------------------- | ------------------- | ----------------------- |
| `ENABLE_TRACING`      | `true`                  | `true`              | Enable/disable tracing  |
| `TRACING_SAMPLE_RATE` | `1.0`                   | `0.05`              | Sampling rate (0.0-1.0) |
| `TRACING_ENDPOINT`    | `http://localhost:4317` | `http://tempo:4317` | Tempo endpoint          |
| `SERVICE_NAME`        | `backend-api`           | `backend-api`       | Service identifier      |
| `SERVICE_VERSION`     | `1.0.0-dev`             | `1.0.0`             | Service version         |

***REMOVED******REMOVED******REMOVED*** **Automatic Service Detection**

The `SERVICE_NAME` is automatically detected from the service directory:

- `apps/backend-api` → `SERVICE_NAME=backend-api`
- `apps/bff-api` → `SERVICE_NAME=bff-api`
- `apps/auth-api` → `SERVICE_NAME=auth-api`

***REMOVED******REMOVED*** 🚀 **Quick Start Examples**

***REMOVED******REMOVED******REMOVED*** **Enable Tracing for One Service**

```bash
***REMOVED*** 1. Start monitoring stack
./scripts/start-monitoring-with-tempo.sh

***REMOVED*** 2. Enable tracing via environment
export ENABLE_TRACING=true

***REMOVED*** 3. Start service (automatically picks up tracing config)
cd apps/backend-api
hatch run python -m uvicorn backend_api.main:create_app --factory --reload --port 8001
```

***REMOVED******REMOVED******REMOVED*** **Enable Tracing for All Services**

```bash
***REMOVED*** Add to infra/.env.local (affects all services)
cat >> infra/.env.local << EOF
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0
TRACING_ENDPOINT=http://localhost:4317
EOF

***REMOVED*** Start services normally - they pick up tracing config
cd apps/backend-api && hatch run uvicorn backend_api.main:create_app --factory &
cd apps/bff-api && hatch run uvicorn bff_api.main:create_app --factory --port 8001 &
```

***REMOVED******REMOVED******REMOVED*** **Production Deployment**

```bash
***REMOVED*** Tracing already configured in infra/.env.production
export ENVIRONMENT=production

***REMOVED*** Deploy services - tracing enabled with 5% sampling
docker-compose up -d
```

***REMOVED******REMOVED*** 🔄 **Dynamic Configuration Changes**

***REMOVED******REMOVED******REMOVED*** **Temporary Sampling Rate Changes**

```bash
***REMOVED*** Increase sampling for debugging (without restart)
export TRACING_SAMPLE_RATE=1.0

***REMOVED*** Restart service to pick up new config
pkill -f "backend_api.main"
cd apps/backend-api && hatch run uvicorn backend_api.main:create_app --factory &
```

***REMOVED******REMOVED******REMOVED*** **Emergency Disable**

```bash
***REMOVED*** Quick disable tracing
export ENABLE_TRACING=false

***REMOVED*** Or set to minimal sampling
export TRACING_SAMPLE_RATE=0.001
```

***REMOVED******REMOVED*** 📋 **Configuration Examples by Environment**

***REMOVED******REMOVED******REMOVED*** **Development (.env.local)**

```bash
***REMOVED*** Development - Full observability
ENVIRONMENT=development
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0
TRACING_ENDPOINT=http://localhost:4317
LOG_LEVEL=DEBUG
```

***REMOVED******REMOVED******REMOVED*** **Staging (.env.staging)**

```bash
***REMOVED*** Staging - Realistic testing
ENVIRONMENT=staging
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.3
TRACING_ENDPOINT=http://tempo-staging:4317
LOG_LEVEL=INFO
```

***REMOVED******REMOVED******REMOVED*** **Production (.env.production)**

```bash
***REMOVED*** Production - Efficient monitoring
ENVIRONMENT=production
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.05
TRACING_ENDPOINT=http://tempo:4317
LOG_LEVEL=INFO
```

***REMOVED******REMOVED*** 🛠️ **Service-Specific Configuration**

***REMOVED******REMOVED******REMOVED*** **Per-Service Overrides**

```bash
***REMOVED*** apps/bff-api/.env.local - Higher sampling for user-facing service
TRACING_SAMPLE_RATE=0.2

***REMOVED*** apps/ml-api/.env.local - Lower sampling for high-volume service
TRACING_SAMPLE_RATE=0.02

***REMOVED*** apps/auth-api/.env.local - Standard sampling for security service
TRACING_SAMPLE_RATE=0.1
```

***REMOVED******REMOVED******REMOVED*** **Docker Compose Override**

```yaml
***REMOVED*** docker-compose.override.yml
services:
  backend-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.1"

  bff-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.2" ***REMOVED*** Higher for user-facing
```

***REMOVED******REMOVED*** ✅ **Validation**

***REMOVED******REMOVED******REMOVED*** **Check Configuration Loading**

```bash
***REMOVED*** Test configuration loading
cd apps/backend-api
python -c "
from backend_api.config.app import BackendAPIConfig
config = BackendAPIConfig()
print(f'Tracing enabled: {config.monitoring.enable_tracing}')
print(f'Sample rate: {config.monitoring.tracing_sample_rate}')
print(f'Endpoint: {config.monitoring.tracing_endpoint}')
"
```

***REMOVED******REMOVED******REMOVED*** **Verify Environment Hierarchy**

```bash
***REMOVED*** Check which files are being loaded
python -c "
from config.env.loader import EnvironmentLoader
loader = EnvironmentLoader()
env_vars = loader.load_environment()
print(f'Loaded files: {loader.loaded_files}')
print(f'Tracing config: {env_vars.get(\"ENABLE_TRACING\", \"not set\")}')
"
```

***REMOVED******REMOVED*** 🎯 **Best Practices**

***REMOVED******REMOVED******REMOVED*** **✅ Do This**

- ✅ Use existing `.env.local` for persistent development settings
- ✅ Use environment variables for temporary/testing changes
- ✅ Use environment-specific files (`.env.development`, `.env.production`)
- ✅ Let services auto-detect their names from directory structure
- ✅ Use the existing NextWatch environment hierarchy

***REMOVED******REMOVED******REMOVED*** **❌ Don't Do This**

- ❌ Create separate `.env.tracing` files (unnecessary complexity)
- ❌ Hardcode tracing configuration in service code
- ❌ Use same sampling rate across all environments
- ❌ Bypass the existing environment loading system

***REMOVED******REMOVED*** 🔍 **Troubleshooting**

***REMOVED******REMOVED******REMOVED*** **Configuration Not Loading**

```bash
***REMOVED*** Check environment loading priority
python -c "
import os
from config.env.loader import load_environment_for_service
env = load_environment_for_service('backend-api')
print('ENABLE_TRACING:', env.get('ENABLE_TRACING'))
print('Files checked:', ['.env', '.env.development', '.env.local'])
"
```

***REMOVED******REMOVED******REMOVED*** **Service Not Picking Up Tracing**

```bash
***REMOVED*** Verify fast-core tracing integration
python -c "
from fast_core.middleware.tracing import setup_tracing
print('✅ Tracing middleware available')
"
```

***REMOVED******REMOVED*** 🎉 **Summary**

**No separate `.env.tracing` files needed!**

NextWatch's existing environment system handles tracing configuration perfectly:

1. **Quick testing**: Use environment variables
2. **Development**: Add to `.env.local`
3. **Production**: Use environment-specific files

The system is **already implemented and working** - just set `ENABLE_TRACING=true` and you're ready to go!
