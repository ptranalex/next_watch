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

The ML API image size varies depending on the build environment:

- **Local build**: Approximately 1.56GB
- **GitHub Actions build**: Approximately 5.95GB

The size difference is primarily due to how PyTorch and its dependencies are handled in different environments. The GitHub Actions build may include CUDA support and additional ML libraries that increase the image size.

***REMOVED******REMOVED******REMOVED*** Optimizing Image Size

To ensure a smaller image size, the Dockerfile uses:

1. A multi-stage build approach
2. CPU-only PyTorch version (specified with `torch==2.7.1+cpu`)
3. Cache directories for ML models to avoid downloading them during build

If you need to further reduce the image size, consider:

- Using a specific, smaller ML model
- Adding more aggressive cleanup steps in the Dockerfile
- Setting environment variables to prevent downloading pre-trained models during build

***REMOVED******REMOVED*** Security

The container runs as a non-root user (`mlapi`) for improved security.
