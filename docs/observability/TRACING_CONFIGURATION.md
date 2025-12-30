# Tracing Configuration Guide

This document shows how to properly enable OpenTelemetry tracing in NextWatch using the **existing environment configuration system**.

## 🎯 **No Separate .env.tracing Files Needed**

NextWatch already has a sophisticated environment management system. **Tracing configuration integrates seamlessly** with the existing `.env` file hierarchy.

## 📁 **Environment File Hierarchy (Existing System)**

NextWatch uses this priority order:

```bash
1. Environment variables (highest priority)
2. .env.local (local development overrides)
3. .env.{environment} (e.g., .env.development, .env.production)
4. .env (base configuration)
5. Default values in code (lowest priority)
```

## 🔧 **How to Enable Tracing**

### **Method 1: Environment Variables (Recommended for Testing)**

```bash
# Quick enable for development
export ENVIRONMENT=development
export ENABLE_TRACING=true
export TRACING_SAMPLE_RATE=1.0

# Start any service - tracing automatically configured
cd apps/backend-api
hatch run python -m uvicorn backend_api.main:create_app --factory
```

### **Method 2: Add to .env.local (Persistent Development)**

```bash
# apps/backend-api/.env.local (or any service)
ENABLE_TRACING=true
TRACING_ENDPOINT=http://localhost:4317
TRACING_SAMPLE_RATE=1.0
SERVICE_NAME=backend-api
```

### **Method 3: Environment-Specific Files (Production)**

Already configured in:

- `infra/.env.development.example` → example dev settings (100% sampling)
- `.env.prod` (Docker Compose production env file) → set `TRACING_SAMPLE_RATE` as desired (commonly 0.05–0.1)

## 📊 **Tracing Configuration Options**

### **Core Settings**

| Variable              | Development             | Production          | Description             |
| --------------------- | ----------------------- | ------------------- | ----------------------- |
| `ENABLE_TRACING`      | `true`                  | `true`              | Enable/disable tracing  |
| `TRACING_SAMPLE_RATE` | `1.0`                   | `0.05`              | Sampling rate (0.0-1.0) |
| `TRACING_ENDPOINT`    | `http://localhost:4317` | `http://tempo:4317` | Tempo endpoint          |
| `SERVICE_NAME`        | `backend-api`           | `backend-api`       | Service identifier      |
| `SERVICE_VERSION`     | `1.0.0-dev`             | `1.0.0`             | Service version         |

### **Automatic Service Detection**

The `SERVICE_NAME` is automatically detected from the service directory:

- `apps/backend-api` → `SERVICE_NAME=backend-api`
- `apps/bff-api` → `SERVICE_NAME=bff-api`
- `apps/auth-api` → `SERVICE_NAME=auth-api`

## 🚀 **Quick Start Examples**

### **Enable Tracing for One Service**

```bash
# 1. Start monitoring stack
./scripts/start-monitoring-with-tempo.sh

# 2. Enable tracing via environment
export ENABLE_TRACING=true

# 3. Start service (automatically picks up tracing config)
cd apps/backend-api
hatch run python -m uvicorn backend_api.main:create_app --factory --reload --port 8001
```

### **Enable Tracing for All Services**

```bash
# Add to each service's local env file (recommended)
cat >> apps/backend-api/.env.local << EOF
ENABLE_TRACING=true
TRACING_ENDPOINT=http://localhost:4317
TRACING_SAMPLE_RATE=1.0
EOF

cat >> apps/bff-api/.env.local << EOF
ENABLE_TRACING=true
TRACING_ENDPOINT=http://localhost:4317
TRACING_SAMPLE_RATE=1.0
EOF
```

### **Production Deployment**

```bash
# Deploy services via Docker Compose
# (ensure .env.prod includes ENABLE_TRACING/TRACING_* variables)
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d
```

## 🔄 **Dynamic Configuration Changes**

### **Temporary Sampling Rate Changes**

```bash
# Increase sampling for debugging (without restart)
export TRACING_SAMPLE_RATE=1.0

# Restart service to pick up new config
pkill -f "backend_api.main"
cd apps/backend-api && hatch run uvicorn backend_api.main:create_app --factory &
```

### **Emergency Disable**

```bash
# Quick disable tracing
export ENABLE_TRACING=false

# Or set to minimal sampling
export TRACING_SAMPLE_RATE=0.001
```

## 📋 **Configuration Examples by Environment**

### **Development (.env.local)**

```bash
# Development - Full observability
ENVIRONMENT=development
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=1.0
TRACING_ENDPOINT=http://localhost:4317
LOG_LEVEL=DEBUG
```

### **Staging (.env.staging)**

```bash
# Staging - Realistic testing
ENVIRONMENT=staging
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.3
TRACING_ENDPOINT=http://tempo-staging:4317
LOG_LEVEL=INFO
```

### **Production (.env.production)**

```bash
# Production - Efficient monitoring
ENVIRONMENT=production
ENABLE_TRACING=true
TRACING_SAMPLE_RATE=0.05
TRACING_ENDPOINT=http://tempo:4317
LOG_LEVEL=INFO
```

## 🛠️ **Service-Specific Configuration**

### **Per-Service Overrides**

```bash
# apps/bff-api/.env.local - Higher sampling for user-facing service
TRACING_SAMPLE_RATE=0.2

# apps/ml-api/.env.local - Lower sampling for high-volume service
TRACING_SAMPLE_RATE=0.02

# apps/auth-api/.env.local - Standard sampling for security service
TRACING_SAMPLE_RATE=0.1
```

### **Docker Compose Override**

Run with the override file:

```bash
docker compose -f infra/compose/prod.yml -f infra/compose/prod.override.yml --env-file .env.prod up -d
```

```yaml
# infra/compose/prod.override.yml
services:
  backend-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.1"

  bff-api:
    environment:
      ENABLE_TRACING: "true"
      TRACING_SAMPLE_RATE: "0.2" # Higher for user-facing
```

## ✅ **Validation**

### **Check Configuration Loading**

```bash
# Test configuration loading
cd apps/backend-api
python -c "
from backend_api.config.app import BackendAPIConfig
config = BackendAPIConfig()
print(f'Tracing enabled: {config.monitoring.enable_tracing}')
print(f'Sample rate: {config.monitoring.tracing_sample_rate}')
print(f'Endpoint: {config.monitoring.tracing_endpoint}')
"
```

### **Verify Environment Hierarchy**

```bash
# Check which files are being loaded
python -c "
from config.env.loader import EnvironmentLoader
loader = EnvironmentLoader()
env_vars = loader.load_environment()
print(f'Loaded files: {loader.loaded_files}')
print(f'Tracing config: {env_vars.get(\"ENABLE_TRACING\", \"not set\")}')
"
```

## 🎯 **Best Practices**

### **✅ Do This**

- ✅ Use existing `.env.local` for persistent development settings
- ✅ Use environment variables for temporary/testing changes
- ✅ Use environment-specific files (`.env.development`, `.env.production`)
- ✅ Let services auto-detect their names from directory structure
- ✅ Use the existing NextWatch environment hierarchy

### **❌ Don't Do This**

- ❌ Create separate `.env.tracing` files (unnecessary complexity)
- ❌ Hardcode tracing configuration in service code
- ❌ Use same sampling rate across all environments
- ❌ Bypass the existing environment loading system

## 🔍 **Troubleshooting**

### **Configuration Not Loading**

```bash
# Check environment loading priority
python -c "
import os
from config.env.loader import load_environment_for_service
env = load_environment_for_service('backend-api')
print('ENABLE_TRACING:', env.get('ENABLE_TRACING'))
print('Files checked:', ['.env', '.env.development', '.env.local'])
"
```

### **Service Not Picking Up Tracing**

```bash
# Verify fast-core tracing integration
python -c "
from fast_core.middleware.tracing import setup_tracing
print('✅ Tracing middleware available')
"
```

## 🎉 **Summary**

**No separate `.env.tracing` files needed!**

NextWatch's existing environment system handles tracing configuration perfectly:

1. **Quick testing**: Use environment variables
2. **Development**: Add to `.env.local`
3. **Production**: Use environment-specific files

The system is **already implemented and working** - just set `ENABLE_TRACING=true` and you're ready to go!
