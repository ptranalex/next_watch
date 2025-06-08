***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.9-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies (only needed for building)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

***REMOVED*** Copy requirements.txt (pre-generated from poetry export)
COPY apps/bff-api/requirements.txt ./

***REMOVED*** Install dependencies to a local directory
RUN pip install --no-cache-dir --user -r requirements.txt

***REMOVED*** Copy application code
COPY apps/bff-api/src ./src/

***REMOVED*** Copy pyproject.toml for package metadata
COPY apps/bff-api/pyproject.toml ./

***REMOVED*** Install the current project to user directory
RUN pip install --no-cache-dir --user -e .

***REMOVED*** Stage 2: Minimal runtime image
FROM python:3.9-alpine AS final

***REMOVED*** Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH" \
    ENVIRONMENT="production" \
    PORT=8001 \
    HOST="0.0.0.0" \
    LOG_LEVEL="info" \
    WORKERS=1 \
    TIMEOUT=120 \
    RELOAD=false \
    PROXY_HEADERS=true \
    FORWARDED_ALLOW_IPS="*" \
    LIMIT_MAX_REQUESTS=10000 \
    BACKLOG=1024

WORKDIR /app

***REMOVED*** Install only runtime dependencies (curl for healthcheck)
RUN apk add --no-cache curl tini

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder (user installation)
COPY --from=builder --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=builder --chown=app:app /app/src ./src/

***REMOVED*** Create logs directory
RUN mkdir -p /app/logs && chown -R app:app /app

USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health/live || exit 1

***REMOVED*** Expose port
EXPOSE 8001

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Run the application using uvicorn directly with proper worker configuration
***REMOVED*** This bypasses our CLI for production to ensure optimal performance
CMD uvicorn bff_api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --timeout-keep-alive ${TIMEOUT} \
    --log-level ${LOG_LEVEL} \
    --no-access-log \
    --proxy-headers ${PROXY_HEADERS} \
    --forwarded-allow-ips ${FORWARDED_ALLOW_IPS} \
    --backlog ${BACKLOG} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS} \
    --reload ${RELOAD} 