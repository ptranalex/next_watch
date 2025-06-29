***REMOVED*** BFF API Dockerfile
***REMOVED*** 
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/bff-api/Dockerfile -t bff-api .
***REMOVED***
***REMOVED*** This Dockerfile requires:
***REMOVED*** - libs/cache/ (NextWatch Cache Library)
***REMOVED*** - libs/cli/ (NextWatch CLI Framework)
***REMOVED*** - libs/config/ (NextWatch Config Library)
***REMOVED*** - libs/fast-core/ (FastAPI Core Framework)
***REMOVED*** - apps/bff-api/ (BFF API application)

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
COPY libs/fast-core ./libs/fast-core/

***REMOVED*** Install local dependencies
RUN pip install --no-cache-dir --user ./libs/cache/ ./libs/cli/ ./libs/config/ ./libs/fast-core/

***REMOVED*** Copy application files
COPY apps/bff-api/pyproject.toml ./pyproject.toml
COPY apps/bff-api/src ./src/

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
    CMD curl -f http://localhost:8000/health/live || exit 1

***REMOVED*** Expose port (following Docker best practice of using 8000 internally)
EXPOSE 8000

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Run the application using uvicorn directly with proper worker configuration
***REMOVED*** This bypasses our CLI for production to ensure optimal performance
CMD ["uvicorn", "bff_api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--timeout-keep-alive", "120", \
     "--log-level", "info", \
     "--no-access-log", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--backlog", "1024", \
     "--limit-max-requests", "10000"] 