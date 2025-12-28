***REMOVED*** Recommendation API Optimized Multi-Stage Dockerfile
***REMOVED***
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/recommendation-api/Dockerfile -t recommendation-api .

***REMOVED*** Stage 1: Base Python with system dependencies (rarely changes)
FROM python:3.12-alpine AS base

WORKDIR /app

***REMOVED*** Install system dependencies with BuildKit cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl \
    tini

***REMOVED*** Stage 2: Python upgrades (occasionally changes)
FROM base AS python-deps

***REMOVED*** Create app user and upgrade pip with cache
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

***REMOVED*** Stage 3: Local dependencies (more frequent changes)
FROM python-deps AS local-deps

***REMOVED*** Copy and install local dependencies with cache mount
COPY libs/fast-core ./libs/fast-core/
COPY libs/config ./libs/config/
COPY libs/cache ./libs/cache/
COPY libs/cli ./libs/cli/
COPY libs/movie-storage ./libs/movie-storage/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user ./libs/fast-core/ ./libs/config/ ./libs/cache/ ./libs/cli/ ./libs/movie-storage/

***REMOVED*** Stage 4: Application dependencies (frequent changes)
FROM local-deps AS app-deps

***REMOVED*** Copy and install app dependencies with cache mount
COPY apps/recommendation-api/pyproject.toml ./pyproject.toml

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -e .

***REMOVED*** Stage 5: Application code (most frequent changes)
FROM app-deps AS app-build

***REMOVED*** Copy application source code (this layer changes most often)
COPY apps/recommendation-api/src ./src/

***REMOVED*** Final stage: Minimal runtime image
FROM python:3.12-alpine AS final

***REMOVED*** Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install runtime dependencies with BuildKit cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache curl tini

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder (user installation)
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
CMD ["python", "-m", "recommendation_api"]
