***REMOVED*** Backend API Dockerfile
***REMOVED*** 
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/backend-api/Dockerfile -t backend-api .
***REMOVED***
***REMOVED*** This Dockerfile requires:
***REMOVED*** - apps/backend-api/ (Backend API application)
***REMOVED*** - libs/cli/ (CLI library)
***REMOVED*** - libs/config/ (Config library)
***REMOVED*** - libs/fast-core/ (Fast-core library for enhanced middleware)

***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies (only needed for building)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

***REMOVED*** Copy local dependencies first
COPY libs/cli ./libs/cli/
COPY libs/config ./libs/config/
COPY libs/fast-core ./libs/fast-core/

***REMOVED*** Install local dependencies
RUN pip install --no-cache-dir --user ./libs/cli/
RUN pip install --no-cache-dir --user ./libs/config/
RUN pip install --no-cache-dir --user ./libs/fast-core/

***REMOVED*** Copy application files
COPY apps/backend-api/pyproject.toml ./pyproject.toml
COPY apps/backend-api/src ./src/

***REMOVED*** Install the current project and its dependencies (local deps are commented out in pyproject.toml)
RUN pip install --no-cache-dir --user -e .

***REMOVED*** Stage 2: Minimal runtime image
FROM python:3.12-alpine AS final

***REMOVED*** Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install only runtime dependencies (curl for healthcheck, postgresql-libs for db connection)
RUN apk add --no-cache curl tini postgresql-libs

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder (user installation)
COPY --from=builder --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=builder --chown=app:app /app/src ./src/

***REMOVED*** Create logs directory with write permissions for app user
RUN mkdir -p /app/logs && chown app:app /app/logs && chmod 755 /app/logs

***REMOVED*** Ensure app directory has correct ownership  
RUN chown -R app:app /app

***REMOVED*** Switch to app user
USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

***REMOVED*** Expose port
EXPOSE 8000

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Run the application using uvicorn directly with proper worker configuration
***REMOVED*** This bypasses our CLI for production to ensure optimal performance
***REMOVED*** Using environment variables for flexibility and consistency
CMD ["sh", "-c", "uvicorn backend_api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --timeout-keep-alive ${TIMEOUT} \
    --log-level ${LOG_LEVEL} \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips \"${FORWARDED_ALLOW_IPS}\" \
    --backlog ${BACKLOG} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS}"] 