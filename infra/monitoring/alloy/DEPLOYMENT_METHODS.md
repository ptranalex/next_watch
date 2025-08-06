***REMOVED*** 🚀 Grafana Alloy Deployment Methods

This directory contains **two deployment methods** for Grafana Alloy observability:

***REMOVED******REMOVED*** 🏭 **Method 1: Production Integrated (Recommended)**

**File**: `../../docker-compose.prod.yml`
**Use Case**: Production deployments via CI/CD

```bash
***REMOVED*** Deploy via GitHub Actions
- Go to Actions → Deploy Application
- Check "Deploy Grafana Alloy (Observability)"
- Run workflow

***REMOVED*** Or deploy manually with full stack
docker-compose -f infra/docker-compose.prod.yml --env-file .env.prod up -d
```

**✅ Benefits:**

- Integrated with CI/CD pipeline
- Coordinated deployment with all services
- Production-ready configuration
- Automatic service discovery

---

***REMOVED******REMOVED*** 🔧 **Method 2: Standalone Development (Testing)**

**File**: `docker-compose.alloy.yml`
**Use Case**: Development, testing, and troubleshooting

```bash
***REMOVED*** Standalone Alloy deployment
cd infra/monitoring/alloy
docker-compose -f docker-compose.alloy.yml up -d
```

**✅ Benefits:**

- Quick testing of Alloy configuration changes
- Independent of main application stack
- Useful for observability troubleshooting
- Educational/reference implementation

---

***REMOVED******REMOVED*** 🎯 **When to Use Each Method**

***REMOVED******REMOVED******REMOVED*** **Use Production Integrated When:**

- ✅ Deploying to production
- ✅ Running the complete NextWatch platform
- ✅ Using CI/CD for deployments
- ✅ Need coordinated service startup

***REMOVED******REMOVED******REMOVED*** **Use Standalone When:**

- 🔧 Testing Alloy configuration changes
- 🔧 Developing observability features
- 🔧 Troubleshooting metrics/logs/traces
- 🔧 Learning how Alloy works
- 🔧 Need observability without full app stack

---

***REMOVED******REMOVED*** 📁 **File Overview**

```
infra/monitoring/alloy/
├── config.alloy                 ***REMOVED*** Alloy configuration (shared)
├── docker-compose.alloy.yml     ***REMOVED*** Standalone deployment
├── .env.example                 ***REMOVED*** Environment template
├── setup-alloy.sh              ***REMOVED*** Setup script (standalone)
└── docs/...                     ***REMOVED*** Documentation

infra/
└── docker-compose.prod.yml      ***REMOVED*** Production deployment (integrated)
```

---

***REMOVED******REMOVED*** 🔄 **Migration Path**

**Current Setup → Recommendation:**

1. **Production**: Use integrated method (`docker-compose.prod.yml`)
2. **Development**: Keep using standalone method for testing
3. **CI/CD**: Updated to deploy integrated Alloy
4. **Documentation**: Updated to reflect both approaches

Both methods use the **same Alloy configuration** (`config.alloy`), ensuring consistency across deployments! 🎯
