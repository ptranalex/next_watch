***REMOVED*** Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

***REMOVED*** Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir hatch && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy only necessary files for wheel build
COPY apps/ml-api/pyproject.toml .
COPY apps/ml-api/ml_api ./ml_api

***REMOVED*** Modify dependencies to use CPU-only PyTorch
RUN sed -i 's/sentence-transformers>=2.2.2/sentence-transformers>=2.2.2/' pyproject.toml

***REMOVED*** Build the wheel package
RUN hatch build -t wheel

***REMOVED*** Stage 2: Runtime
FROM python:3.12-slim

***REMOVED*** Environment variables for runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    EMBEDDING_MODEL="all-MiniLM-L6-v2" \
    TORCH_HOME="/app/.cache/torch" \
    TRANSFORMERS_CACHE="/app/.cache/transformers" \
    SENTENCE_TRANSFORMERS_HOME="/app/.cache/sentence_transformers" \
    ENVIRONMENT="production" \
    PORT=8000 \
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

***REMOVED*** Create a non-root user
RUN useradd -m -r mlapi

***REMOVED*** Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl tini && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy and install the built wheel only
COPY --from=builder /build/dist/*.whl .

***REMOVED*** Install with explicit CPU-only dependencies
RUN pip install --no-cache-dir ./*.whl && \
    pip install --no-cache-dir torch==2.7.1+cpu --index-url https://download.pytorch.org/whl/cpu && \
    rm -f ./*.whl

***REMOVED*** Set file ownership and permissions
RUN mkdir -p /app/.cache && chown -R mlapi:mlapi /app

***REMOVED*** Switch to non-root user
USER mlapi

***REMOVED*** Expose the application port (following Docker best practice of using 8000 internally)
EXPOSE 8000

***REMOVED*** Healthcheck with curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Start the application with uvicorn and proxy header configuration
CMD uvicorn ml_api.app:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --timeout-keep-alive ${TIMEOUT} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS} \
    --proxy-headers ${PROXY_HEADERS} \
    --no-access-log \
    --forwarded-allow-ips ${FORWARDED_ALLOW_IPS} \
    --backlog ${BACKLOG} \
    --reload ${RELOAD}