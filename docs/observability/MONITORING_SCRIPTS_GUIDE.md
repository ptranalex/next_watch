# NextWatch Monitoring Scripts Guide

This guide explains when and how to use the different monitoring scripts in the NextWatch project.

## 📋 Script Overview

| Script                                                | Purpose               | Environment                 | Tempo Included |
| ----------------------------------------------------- | --------------------- | --------------------------- | -------------- |
| `scripts/start-monitoring-with-tempo.sh`              | Local development     | Docker on developer machine | ✅ Yes         |
| `infra/aws/deployment/deploy-monitoring-one-click.sh` | Production deployment | AWS EC2 instances           | ✅ Yes         |

## 🏠 Local Development: `start-monitoring-with-tempo.sh`

**When to use**: When developing locally and want to test monitoring/tracing

### Features:

- Sets up complete monitoring stack on your local machine
- Includes Grafana Tempo for distributed tracing
- Uses localhost endpoints and development-friendly settings
- Interactive and verbose output for debugging

### Usage:

```bash
# From project root
./scripts/start-monitoring-with-tempo.sh

# Then start your services with tracing enabled (example)
export ENABLE_TRACING=true
export TRACING_ENDPOINT=http://localhost:4317
export TRACING_SAMPLE_RATE=1.0
cd apps/backend-api && hatch run python -m backend_api
```

### Access:

- **Grafana**: http://localhost:3001 (admin/admin)
- **Tempo**: http://localhost:3200
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

---

## 🚀 Production Deployment: `deploy-monitoring-one-click.sh`

**When to use**: When deploying to AWS production infrastructure

### Features:

- Deploys to existing AWS EC2 instances
- Configures security groups and networking
- Sets up SSL/TLS and production domains
- Includes all monitoring components **including Tempo**
- Production-optimized configurations
- Automated health checks and verification

### Usage:

```bash
# From project root
./infra/aws/deployment/deploy-monitoring-one-click.sh
```

### What it does:

1. ✅ **Environment Check**: Verifies AWS credentials and instance
2. 🔓 **Security Groups**: Opens monitoring ports (3001, 9090, 9093, 3100, 3200)
3. 🐳 **Deploy Stack**: Deploys complete monitoring with **Tempo included**
4. 🔍 **Configure Tracing**: Sets up OpenTelemetry for all services

### Access:

- **Grafana**: `https://your-domain.com/grafana/`
- **Tempo**: http://YOUR_IP:3200
- **Prometheus**: http://YOUR_IP:9090
- **Other services**: Various ports on your AWS instance

---

## 🤔 Why Two Scripts?

### Historical Context

Originally, we had separate scripts because:

- Local development needs different configurations than production
- AWS deployment requires additional setup (security groups, networking)
- Different storage backends (local files vs. production volumes)

### Current State (Post-Tempo Integration)

**Both scripts now include Tempo**, but serve different purposes:

| Aspect             | Local Script           | Production Script     |
| ------------------ | ---------------------- | --------------------- |
| **Target**         | Developer workstation  | AWS EC2               |
| **Configuration**  | Development-friendly   | Production-optimized  |
| **Networking**     | localhost              | Public IPs + domains  |
| **Security**       | Minimal                | SSL + security groups |
| **Persistence**    | Local Docker volumes   | AWS EBS volumes       |
| **Trace Sampling** | 50% (high for testing) | 10% (production rate) |

---

## 🎯 Recommendation: Use the Right Tool

### For Local Development:

```bash
./scripts/start-monitoring-with-tempo.sh
```

- ✅ Quick setup
- ✅ Development-friendly settings
- ✅ Easy to iterate and debug

### For Production:

```bash
./infra/aws/deployment/deploy-monitoring-one-click.sh
```

- ✅ Complete AWS integration
- ✅ Production security and performance
- ✅ SSL and proper networking
- ✅ **Includes Tempo automatically**

---

## 🔄 Future Improvements

To reduce script duplication, we could:

1. **Extract Common Logic**: Create shared functions for Docker operations
2. **Environment-Specific Configs**: Use environment templates instead of separate scripts
3. **Unified Script**: Single script with `--environment=local|production` flag

However, the current approach provides:

- ✅ Clear separation of concerns
- ✅ Environment-specific optimizations
- ✅ Easy maintenance and understanding

---

## 📚 Related Documentation

- [Tempo Integration Guide](./TEMPO_INTEGRATION.md)
- [Production Monitoring Deployment](./PRODUCTION_MONITORING_DEPLOYMENT.md)
- [Environment Configuration](./environment-config.md)
