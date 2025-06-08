***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="${PATH}:/root/.local/bin"

WORKDIR /app

***REMOVED*** Install build dependencies - use a single layer and clean up in the same step
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    curl \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir hatch

***REMOVED*** Copy only dependency-related files first
COPY libs/movie-storage /tmp/movie-storage/
COPY apps/backend-api/pyproject.toml apps/backend-api/hatch.toml ./

***REMOVED*** Install the movie-storage package first
WORKDIR /tmp/movie-storage
RUN pip install -e .

***REMOVED*** Return to app directory and install application
WORKDIR /app
COPY apps/backend-api/src ./src/

***REMOVED*** Install the application
RUN pip install --no-cache-dir -e .

***REMOVED*** Stage 2: Runtime image - use a much smaller base
FROM python:3.12-alpine AS final

***REMOVED*** Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src \
    ENVIRONMENT="production" \
    PORT=8000 \
    HOST="0.0.0.0" \
    LOG_LEVEL="info" \
    WORKERS=1 \
    TIMEOUT=120 \
    MAX_KEEPALIVE=60 \
    RELOAD=false \
    PROXY_HEADERS=true \
    FORWARDED_ALLOW_IPS="*" \
    LIMIT_MAX_REQUESTS=10000 \
    BACKLOG=1024

WORKDIR /app

***REMOVED*** Install runtime dependencies including tini for proper process handling
RUN apk add --no-cache libstdc++ curl tini

***REMOVED*** Copy the installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

***REMOVED*** Copy the movie-storage package
COPY --from=builder /tmp/movie-storage /app/movie-storage
RUN pip install -e /app/movie-storage

***REMOVED*** Only copy the application code, not the entire Python installation
COPY apps/backend-api/src ./src/

EXPOSE 8000

***REMOVED*** Use a non-root user for better security
RUN addgroup -S app && adduser -S app -G app

***REMOVED*** Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app

USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Run the application with production optimizations
***REMOVED*** Hardcode log-level=info, proxy_headers=true and no reload for production
CMD uvicorn backend_api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --timeout-keep-alive ${TIMEOUT} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS} \
    --no-access-log \
    --backlog ${BACKLOG} \
    --proxy-headers \
    --forwarded-allow-ips "*" 