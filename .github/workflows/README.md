# GitHub Actions Workflows

This directory contains the CI/CD workflows for the NextWatch microservices platform. We use a **hybrid runner strategy** that optimizes for both performance and cost.

## 🎯 **Hybrid Runner Strategy**

| Runner Type          | Services    | Workflow                    | Why                                        |
| -------------------- | ----------- | --------------------------- | ------------------------------------------ |
| **☁️ GitHub-Hosted** | 7 services  | `build-app.yml`             | Fast, cost-effective, zero maintenance     |
| **🏗️ Self-Hosted**   | ML API only | `build-app-self-hosted.yml` | Heavy models, GPU access, persistent cache |

## 📂 **Workflow Files**

### **Core Build Workflows**

#### `build.yml` - Main Build Orchestrator

- **Purpose**: Main entry point for all builds
- **Triggers**: Push to main, manual dispatch, workflow_call
- **Function**: Detects changes and routes to appropriate build workflows
- **Services**: Routes all 8 microservices to their optimal runners

#### `build-app.yml` - Default GitHub-Hosted Build

- **Purpose**: Standard build workflow (DEFAULT)
- **Runner**: `ubuntu-latest` (GitHub-hosted)
- **Used By**:
  - `backend-api` - Core movie data API
  - `auth-api` - Authentication service
  - `bff-api` - Backend-for-Frontend (cache warming!)
  - `web-nextjs` - Frontend application
  - `data-importer` - Movie data ingestion
  - `recommendation-api` - Recommendation API layer
  - `search-api` - Search functionality
- **Features**: GitHub Actions cache, fast parallel builds, cosign signing

#### `build-app-self-hosted.yml` - ML-Specific Build

- **Purpose**: Resource-intensive builds (EXCEPTION)
- **Runner**: `[self-hosted, nextwatch]`
- **Used By**:
  - `ml-api` - Machine learning embeddings service
- **Features**: Local cache, GPU access, model downloads, persistent storage

### **Deployment Workflows**

#### `deploy.yml` - Production Deployment

- **Purpose**: Deploy services to production
- **Trigger**: Manual dispatch with service selection
- **Method**: SSH-based deployment to production server
- **Features**: Individual service control, comprehensive secrets management

#### `release.yml` - Automated Release Pipeline

- **Purpose**: Full CI/CD pipeline (build + deploy)
- **Trigger**: Push to main branch (path-based)
- **Flow**: Build → Deploy automatically
- **Safety**: Path-based triggering (only affected services)

### **Data Operations**

#### `sync-movies.yml` - Movie Data Import

- **Purpose**: Import movie data from external APIs (TMDB, OMDB)
- **Trigger**: Manual dispatch
- **Features**: Configurable year ranges, batch limits, credits inclusion

#### `sync-redis-suggestions.yml` - Search Cache Population

- **Purpose**: Populate Redis with search suggestions
- **Trigger**: Manual dispatch
- **Features**: Actors, directors, movies with configurable limits

## 🚀 **Usage Examples**

### **Manual Builds**

```bash
# Build all services (force)
gh workflow run build.yml -f build_all=true

# Build specific service (automatic detection)
echo "fix: update cache warming" >> apps/bff-api/README.md
git add . && git commit -m "Update BFF API"
git push  # Automatically builds only BFF API with GitHub-hosted runner

# Build ML service (automatic detection)
echo "feat: improve embeddings" >> apps/ml-api/README.md
git add . && git commit -m "Update ML API"
git push  # Automatically builds only ML API with self-hosted runner
```

### **Manual Deployments**

```bash
# Deploy specific services
gh workflow run deploy.yml \
  -f deploy_bff=true \
  -f deploy_backend=true

# Deploy everything
gh workflow run deploy.yml \
  -f deploy_backend=true \
  -f deploy_auth=true \
  -f deploy_bff=true \
  -f deploy_frontend=true \
  -f deploy_importer=true \
  -f deploy_recommendation=true \
  -f deploy_search=true \
  -f deploy_ml=true
```

### **Data Operations**

```bash
# Import recent movies
gh workflow run sync-movies.yml \
  -f start_year=2023 \
  -f end_year=2024 \
  -f limit=200

# Refresh search suggestions
gh workflow run sync-redis-suggestions.yml \
  -f limit=1000 \
  -f clear=true
```

## 🏗️ **Architecture Decisions**

### **Why Hybrid Runners?**

#### **GitHub-Hosted Benefits (7 services)**

- ✅ **Cost Effective**: Pay per minute usage
- ✅ **Zero Maintenance**: Fully managed infrastructure
- ✅ **Fast Parallel Builds**: 20+ concurrent builds
- ✅ **Latest Tools**: Always updated build environment
- ✅ **Security**: Isolated environments per build

#### **Self-Hosted Benefits (ML API only)**

- ✅ **Performance**: ~3-5 min builds vs 8-10 min
- ✅ **Persistent Cache**: Model downloads cached locally
- ✅ **GPU Access**: Future ML acceleration capabilities
- ✅ **Memory**: Sufficient RAM for large model loading
- ✅ **Custom Environment**: ML-specific optimizations

### **Service-Specific Rationale**

| Service                | Runner Choice | Reasoning                                                    |
| ---------------------- | ------------- | ------------------------------------------------------------ |
| **ml-api**             | Self-hosted   | 📦 90MB+ model downloads, 🧠 200MB+ memory, ⚡ GPU potential |
| **bff-api**            | GitHub-hosted | 🚀 Standard FastAPI, cache warming logic, frequent changes   |
| **backend-api**        | GitHub-hosted | 🗄️ Standard database API, no heavy dependencies              |
| **auth-api**           | GitHub-hosted | 🔐 Lightweight auth service, security focus                  |
| **web-nextjs**         | GitHub-hosted | 🎨 Frontend builds great on GitHub Actions                   |
| **search-api**         | GitHub-hosted | 🔍 Redis-based, fast builds                                  |
| **recommendation-api** | GitHub-hosted | 📊 API layer only, no model training                         |
| **data-importer**      | GitHub-hosted | 📥 Python scripts, standard dependencies                     |

## 📊 **Performance Metrics**

### **Build Times**

- **GitHub-Hosted Services**: ~5-8 minutes
- **Self-Hosted ML**: ~3-5 minutes
- **Total Pipeline**: ~8-10 minutes (parallel execution)

### **Cost Impact**

- **Before**: 8 services × self-hosted overhead = High fixed costs
- **After**: 1 self-hosted + 7 pay-per-minute = ~60-70% savings

## 🔧 **Maintenance**

### **Adding New Services**

1. Add to `build.yml` using `build-app.yml` (GitHub-hosted default)
2. Only use `build-app-self-hosted.yml` if service requires heavy resources

### **Moving Services Between Runners**

```yaml
# To move a service from GitHub-hosted to self-hosted:
build_service_name:
  uses: ./.github/workflows/build-app-self-hosted.yml  # Change this line

# To move from self-hosted to GitHub-hosted:
build_service_name:
  uses: ./.github/workflows/build-app.yml  # Change this line
```

### **Monitoring**

- **GitHub Actions Tab**: Monitor build status and times
- **Self-Hosted Runner**: Monitor via runner dashboard
- **Costs**: Track GitHub Actions usage in billing

## 🚨 **Troubleshooting**

### **Common Issues**

#### **GitHub-Hosted Builds Failing**

```bash
# Check GitHub Actions cache
gh workflow run build.yml -f build_all=true

# Clear cache if needed (rebuild from scratch)
# Cache automatically expires after 7 days
```

#### **Self-Hosted Runner Issues**

```bash
# Check runner status
# Navigate to Settings > Actions > Runners in GitHub

# Restart runner if needed
sudo systemctl restart actions.runner.nextwatch.service
```

#### **ML Model Download Failures**

```bash
# Check model cache directory on self-hosted runner
ls -la /tmp/buildkit-cache/ml-api/

# Clear cache if corrupted
rm -rf /tmp/buildkit-cache/ml-api/
```

## 📝 **Development Guidelines**

### **Best Practices**

1. **Default to GitHub-hosted** for new services
2. **Use self-hosted only** for resource-intensive workloads
3. **Test builds locally** before pushing to main
4. **Monitor build times** and optimize as needed
5. **Keep workflows DRY** by using reusable workflows

### **When to Use Each Runner**

- **GitHub-Hosted**: Standard APIs, web apps, lightweight services
- **Self-Hosted**: ML models, large downloads, GPU needs, persistent cache benefits

---

**📚 For more details, see [CI_CD_HYBRID_STRATEGY.md](CI_CD_HYBRID_STRATEGY.md)**
