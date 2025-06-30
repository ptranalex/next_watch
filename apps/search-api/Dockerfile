***REMOVED*** Optimized Search API Dockerfile for fast builds
***REMOVED*** 
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/search-api/Dockerfile -t search-api .
***REMOVED***
***REMOVED*** Optimization Strategy:
***REMOVED*** 1. Maximize layer caching by ordering operations by change frequency
***REMOVED*** 2. Use BuildKit cache mounts for package downloads  
***REMOVED*** 3. Separate dependency installation from app code for better caching
***REMOVED*** 4. Use multi-stage builds to minimize final image size

***REMOVED*** Stage 1: Base Python with system dependencies (changes rarely)
FROM python:3.12-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ***REMOVED*** Build optimization
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

***REMOVED*** Install system dependencies with cache mounts (cached layer - changes rarely)
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl \
    tini

***REMOVED*** Stage 2: Python dependencies (changes occasionally)
FROM base AS python-deps

***REMOVED*** Create user early for consistent permissions
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Install pip and setuptools upgrades (cached layer)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

***REMOVED*** Stage 3: Local dependencies (changes more frequently than base deps)
FROM python-deps AS local-deps

***REMOVED*** Copy and install local libraries (order by change frequency)
COPY libs/fast-core ./libs/fast-core/
COPY libs/config ./libs/config/
COPY libs/cache ./libs/cache/
COPY libs/cli ./libs/cli/

***REMOVED*** Install local dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user ./libs/fast-core/ ./libs/config/ ./libs/cache/ ./libs/cli/

***REMOVED*** Stage 4: App dependencies (changes frequently)
FROM local-deps AS app-deps

***REMOVED*** Copy only pyproject.toml first (dependency specification)
COPY apps/search-api/pyproject.toml ./pyproject.toml

***REMOVED*** Install app dependencies with cache mount (but not the app itself yet)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -e .

***REMOVED*** Stage 5: Application code (changes most frequently)  
FROM app-deps AS app-build

***REMOVED*** Copy application source code (this layer changes most often)
COPY apps/search-api/src ./src/

***REMOVED*** Final stage: Minimal runtime image
FROM python:3.12-alpine AS final

***REMOVED*** Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install only runtime dependencies with cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache curl tini

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder (all dependencies)
COPY --from=app-build --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=app-build --chown=app:app /app/src ./src/

***REMOVED*** Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app

USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

***REMOVED*** Expose port (following Docker best practice of using 8000 internally)
EXPOSE 8000

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Run the application using Python module entry point
***REMOVED*** This allows the app to use its own settings configuration
***REMOVED*** rather than manually passing uvicorn parameters
CMD ["python", "-m", "search_api.main"] 