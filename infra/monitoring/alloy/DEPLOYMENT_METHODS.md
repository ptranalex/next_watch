# 🚀 Grafana Alloy Deployment Methods

This directory contains **two deployment methods** for Grafana Alloy observability:

## 🏭 **Method 1: Production Integrated (Recommended)**

**File**: `../../compose/prod.yml`
**Use Case**: Production deployments via CI/CD

```bash
# Deploy via GitHub Actions
- Go to Actions → Deploy Application
- Check "Deploy Grafana Alloy (Observability)"
- Run workflow

# Or deploy manually with full stack
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d
```

**✅ Benefits:**

- Integrated with CI/CD pipeline
- Coordinated deployment with all services
- Production-ready configuration
- Automatic service discovery

---

## 🔧 **Method 2: Standalone Development (Testing)**

**File**: `docker-compose.alloy.yml`
**Use Case**: Development, testing, and troubleshooting

```bash
# Standalone Alloy deployment
cd infra/monitoring/alloy
docker compose -f docker-compose.alloy.yml up -d
```

**✅ Benefits:**

- Quick testing of Alloy configuration changes
- Independent of main application stack
- Useful for observability troubleshooting
- Educational/reference implementation

---

## 🎯 **When to Use Each Method**

### **Use Production Integrated When:**

- ✅ Deploying to production
- ✅ Running the complete NextWatch platform
- ✅ Using CI/CD for deployments
- ✅ Need coordinated service startup

### **Use Standalone When:**

- 🔧 Testing Alloy configuration changes
- 🔧 Developing observability features
- 🔧 Troubleshooting metrics/logs/traces
- 🔧 Learning how Alloy works
- 🔧 Need observability without full app stack

---

## 📁 **File Overview**

```
infra/monitoring/alloy/
├── config.alloy                 # Alloy configuration (shared)
├── docker-compose.alloy.yml     # Standalone deployment
├── .env.example                 # Environment template
├── setup-alloy.sh              # Setup script (standalone)
└── docs/...                     # Documentation

infra/
└── compose/prod.yml             # Production deployment (integrated)
```

---

## 🔄 **Migration Path**

**Current Setup → Recommendation:**

1. **Production**: Use integrated method (`infra/compose/prod.yml`)
2. **Development**: Keep using standalone method for testing
3. **CI/CD**: Updated to deploy integrated Alloy
4. **Documentation**: Updated to reflect both approaches

Both methods use the **same Alloy configuration** (`config.alloy`), ensuring consistency across deployments! 🎯
