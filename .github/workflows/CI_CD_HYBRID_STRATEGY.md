***REMOVED*** CI/CD Hybrid Runner Strategy

***REMOVED******REMOVED*** 🎯 **Strategy Overview**

**ML API**: Self-hosted runners (resource-intensive, model downloads, GPU access)
**All other services**: GitHub-hosted runners (cost-effective, fast, managed)

***REMOVED******REMOVED*** 📊 **Runner Assignment**

| Service                | Runner Type      | Workflow                      | Reasoning                              |
| ---------------------- | ---------------- | ----------------------------- | -------------------------------------- |
| **ml-api**             | 🏗️ Self-hosted   | `build-app.yml`               | Heavy ML models, embeddings, GPU needs |
| **backend-api**        | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Standard API, fast builds              |
| **auth-api**           | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Lightweight service                    |
| **bff-api**            | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Our cache warming service!             |
| **web-nextjs**         | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Frontend, good GitHub Actions support  |
| **data-importer**      | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Python service, standard build         |
| **recommendation-api** | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | API layer, not model training          |
| **search-api**         | ☁️ GitHub-hosted | `build-app-github-hosted.yml` | Fast Redis-based service               |

***REMOVED******REMOVED*** 💰 **Cost & Performance Benefits**

***REMOVED******REMOVED******REMOVED*** **Self-Hosted (ML only)**

- **Cost**: Fixed hardware cost
- **Performance**: ⚡ ~3-5 min builds
- **Specialized**: GPU access, large model downloads
- **Maintenance**: You manage

***REMOVED******REMOVED******REMOVED*** **GitHub-Hosted (Everything else)**

- **Cost**: Pay-per-minute (but 7 services × shorter builds)
- **Performance**: 🚀 ~5-8 min builds
- **Managed**: Zero maintenance
- **Scalability**: 20+ concurrent builds

***REMOVED******REMOVED*** 🔄 **Migration Plan**

***REMOVED******REMOVED******REMOVED*** **Phase 1: Update Workflows** ✅ COMPLETED

1. ✅ Keep existing `build-app.yml` for ML
2. ✅ Use new `build-app-github-hosted.yml` for others
3. ✅ Updated existing `build.yml` (not a new file)

***REMOVED******REMOVED******REMOVED*** **Phase 2: Test & Validate**

```bash
***REMOVED*** Test individual services
gh workflow run build.yml -f build_all=true

***REMOVED*** Test ML specifically (should use self-hosted)
echo "test" >> apps/ml-api/README.md && git add . && git commit -m "test ML build"

***REMOVED*** Test other services (should use GitHub-hosted)
echo "test" >> apps/bff-api/README.md && git add . && git commit -m "test BFF build"
```

***REMOVED******REMOVED******REMOVED*** **Phase 3: Update Release Pipeline**

✅ No changes needed - `release.yml` already calls `build.yml`

***REMOVED******REMOVED*** 🎯 **Why This Makes Sense**

***REMOVED******REMOVED******REMOVED*** **ML API Needs Self-Hosted Because:**

- 📦 **Large Model Downloads**: `all-MiniLM-L6-v2` embeddings
- 🧠 **Memory Requirements**: ML model loading
- ⚡ **GPU Access**: Potential future GPU acceleration
- 🏗️ **Build Cache**: Persistent model/dependency cache
- 🔧 **Custom Environment**: ML-specific optimizations

***REMOVED******REMOVED******REMOVED*** **Other Services Work Great on GitHub-Hosted:**

- 🚀 **Fast Builds**: Most are lightweight Python/Node.js
- 💰 **Cost Effective**: Pay only for what you use
- 🔧 **Zero Maintenance**: No runner management
- 📈 **Better Scalability**: Multiple PRs can build simultaneously
- 🛡️ **Security**: Isolated environments per build

***REMOVED******REMOVED*** 📋 **Implementation Steps**

***REMOVED******REMOVED******REMOVED*** **1. Update Main Build Workflow**

```bash
***REMOVED*** Rename current build workflow
mv .github/workflows/build.yml .github/workflows/build-legacy.yml

***REMOVED*** Use the new optimized workflow
mv .github/workflows/build-optimized.yml .github/workflows/build.yml
```

***REMOVED******REMOVED******REMOVED*** **2. Update Release Workflow**

In `.github/workflows/release.yml`, ensure it calls the updated `build.yml`

***REMOVED******REMOVED******REMOVED*** **3. Test the Migration**

```bash
***REMOVED*** Test with a small change to each service type
echo "test" >> apps/bff-api/README.md      ***REMOVED*** Should use GitHub-hosted
echo "test" >> apps/ml-api/README.md       ***REMOVED*** Should use self-hosted
```

***REMOVED******REMOVED*** 🚨 **Special Considerations**

***REMOVED******REMOVED******REMOVED*** **ML API Build Requirements**

- **Build Args**:
  ```yaml
  EMBEDDING_MODEL=all-MiniLM-L6-v2
  ENABLE_METRICS=true
  ENVIRONMENT=production
  ```
- **Persistent Cache**: Benefits from self-hosted local cache
- **Network**: May need model downloads from HuggingFace

***REMOVED******REMOVED******REMOVED*** **BFF API (Our Cache Warming Service)**

- ✅ **Perfect for GitHub-hosted**: Standard Python FastAPI
- ✅ **Fast builds**: No heavy dependencies
- ✅ **Cost effective**: Frequent changes during development
- ✅ **Concurrent builds**: Multiple PRs can test cache warming

***REMOVED******REMOVED*** 🎉 **Expected Results**

***REMOVED******REMOVED******REMOVED*** **Build Times**

- **ML API**: ~3-5 minutes (self-hosted, optimized cache)
- **Other APIs**: ~5-8 minutes (GitHub-hosted, parallel builds)
- **Total pipeline**: ~8-10 minutes (parallel execution)

***REMOVED******REMOVED******REMOVED*** **Cost Savings**

- **Before**: 8 services × self-hosted overhead
- **After**: 1 service self-hosted + 7 services pay-per-minute
- **Estimated savings**: 60-70% on CI/CD costs

***REMOVED******REMOVED******REMOVED*** **Development Velocity**

- ✅ **Faster PR builds**: GitHub-hosted parallel execution
- ✅ **Less maintenance**: 7/8 services fully managed
- ✅ **Better reliability**: GitHub's infrastructure
- ✅ **Easier debugging**: Standard GitHub Actions environment

***REMOVED******REMOVED*** 🛠️ **Rollback Plan**

If issues arise, easy rollback:

```bash
***REMOVED*** Emergency rollback to full self-hosted
mv .github/workflows/build.yml .github/workflows/build-optimized.yml
mv .github/workflows/build-legacy.yml .github/workflows/build.yml
```

---

**Status**: ✅ **READY** - Hybrid strategy optimizes for ML workloads while maximizing efficiency for standard services.
