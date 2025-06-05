***REMOVED*** ML API Docker Build Guide

This document explains how to properly build and run the ML API Docker container.

***REMOVED******REMOVED*** Prerequisites

- Docker installed on your system
- Access to the Next Watch monorepo

***REMOVED******REMOVED*** Building the Docker Image

The ML API Dockerfile is designed to be built from the monorepo root to access all dependencies.

***REMOVED******REMOVED******REMOVED*** Building from Monorepo Root

Always build the Docker image from the monorepo root directory:

```bash
***REMOVED*** From the monorepo root (/Users/alex/Sandbox/next_watch)
docker build -t ml-api:latest -f apps/ml-api/Dockerfile .
```

This ensures that all dependencies are correctly included in the build.

***REMOVED******REMOVED*** Running the Container

Once built, you can run the ML API container with:

```bash
docker run -d --name ml-api -p 8004:8004 ml-api:latest
```

***REMOVED******REMOVED******REMOVED*** Health Check

The container includes a health check endpoint that can be accessed at:

```bash
curl http://localhost:8004/health
```

Note that the ML API may take some time to initialize as it loads the machine learning model. The health check has a 5-second start period to account for this.

***REMOVED******REMOVED*** Image Size and Optimization

The ML API image is approximately 1.56GB due to the inclusion of machine learning dependencies like sentence-transformers. This is expected for an ML-based container.

The Dockerfile uses a multi-stage build approach to minimize the final image size:

1. Builder stage: Builds the Python wheel package
2. Runtime stage: Installs only the necessary runtime dependencies

***REMOVED******REMOVED*** Security

The container runs as a non-root user (`mlapi`) for improved security.
