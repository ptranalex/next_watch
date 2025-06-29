***REMOVED*** Recommendation API Dockerfile
***REMOVED*** 
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/recommendation-api/Dockerfile -t recommendation-api .

***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies (only needed for building)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

***REMOVED*** Copy local dependencies first
COPY libs/cache ./libs/cache/
COPY libs/cli ./libs/cli/
COPY libs/config ./libs/config/
COPY libs/movie-storage ./libs/movie-storage/
COPY libs/fast-core ./libs/fast-core/

***REMOVED*** Install local dependencies
RUN pip install --no-cache-dir --user ./libs/cache/ ./libs/cli/ ./libs/config/ ./libs/movie-storage/ ./libs/fast-core/ ./libs/fast-core/

***REMOVED*** Copy application files
COPY apps/recommendation-api/pyproject.toml ./pyproject.toml
COPY apps/recommendation-api/src ./src/

***REMOVED*** Install the current project and its dependencies (local deps are commented out in pyproject.toml)
RUN pip install --no-cache-dir --user -e .

***REMOVED*** Stage 2: Minimal runtime image
FROM python:3.12-alpine AS final

***REMOVED*** Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH" \
    ENVIRONMENT="production" \
    PORT=8000 \
    HOST="0.0.0.0" \
    LOG_LEVEL="info" \
    LOGS_DIR="/app/logs" \
    WORKERS=1 \
    TIMEOUT=120 \
    MAX_KEEPALIVE=60 \
    RELOAD=false \
    PROXY_HEADERS=true \
    FORWARDED_ALLOW_IPS="*" \
    LIMIT_MAX_REQUESTS=10000 \
    BACKLOG=1024 \
    ENABLE_CACHING=true \
    CACHE_TTL_DEFAULT=3600 \
    CACHE_KEY_PREFIX=recommendation

WORKDIR /app

***REMOVED*** Install runtime dependencies including tini for proper process handling
RUN apk add --no-cache curl tini

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder (user installation)
COPY --from=builder --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=builder --chown=app:app /app/src ./src/

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

***REMOVED*** Run the application with production optimizations
***REMOVED*** Use environment variables for host and port to allow for flexibility
CMD uvicorn recommendation_api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --timeout-keep-alive ${MAX_KEEPALIVE} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS} \
    --no-access-log \
    --backlog ${BACKLOG} \
    --proxy-headers \
    --forwarded-allow-ips "${FORWARDED_ALLOW_IPS}" 