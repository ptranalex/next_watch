***REMOVED*** ML API Dockerfile
***REMOVED*** 
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/ml-api/Dockerfile -t ml-api .
***REMOVED***
***REMOVED*** This Dockerfile requires:
***REMOVED*** - libs/cache/ (NextWatch Cache Library) - optional for ML API
***REMOVED*** - libs/cli/ (NextWatch CLI Framework)
***REMOVED*** - libs/config/ (NextWatch Config Library)
***REMOVED*** - libs/fast-core/ (FastAPI Core Framework)
***REMOVED*** - apps/ml-api/ (ML API application)

***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies (needed for ML packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy local dependencies first
COPY libs/cli ./libs/cli/
COPY libs/config ./libs/config/
COPY libs/fast-core ./libs/fast-core/

***REMOVED*** Install local dependencies
RUN pip install --no-cache-dir --user ./libs/cli/ ./libs/config/ ./libs/fast-core/

***REMOVED*** Copy the pyproject.toml file
COPY apps/ml-api/pyproject.toml ./pyproject.toml

***REMOVED*** Install dependencies first, then install CPU-only PyTorch
RUN pip install --no-cache-dir --user -e . && \
pip install --no-cache-dir --user --force-reinstall torch==2.7.1+cpu --index-url https://download.pytorch.org/whl/cpu

***REMOVED*** Copy application files
COPY apps/ml-api/src ./src/

***REMOVED*** Stage 2: Minimal runtime image
FROM python:3.12-slim AS final

***REMOVED*** Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH" \
    ENVIRONMENT="production" \
    PORT=8004 \
    HOST="0.0.0.0" \
    LOG_LEVEL="info" \
    WORKERS=1 \
    TIMEOUT=120 \
    RELOAD=false \
    PROXY_HEADERS=true \
    FORWARDED_ALLOW_IPS="*" \
    LIMIT_MAX_REQUESTS=10000 \
    BACKLOG=1024 \
    ***REMOVED*** ML-specific environment variables
    EMBEDDING_MODEL="all-MiniLM-L6-v2" \
    TORCH_HOME="/app/.cache/torch" \
    TRANSFORMERS_CACHE="/app/.cache/transformers" \
    SENTENCE_TRANSFORMERS_HOME="/app/.cache/sentence_transformers" \
    ***REMOVED*** Configuration variables (JSON format for Pydantic)
    SERVICE_NAME="ml-api" \
    CORS_ORIGINS='["*"]' \
    ALLOWED_HOSTS='["*"]' \
    ENABLE_EMBEDDINGS=true \
    ENABLE_BATCH_PROCESSING=true \
    ENABLE_MODEL_CACHING=true \
    ENABLE_METRICS=true

WORKDIR /app

***REMOVED*** Install only runtime dependencies (curl for healthcheck, tini for signal handling)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/*

***REMOVED*** Create app user
RUN groupadd -r app && useradd -r -g app app

***REMOVED*** Copy Python packages from builder (user installation)
COPY --from=builder --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=builder --chown=app:app /app/src ./src/

***REMOVED*** Create necessary directories
RUN mkdir -p /app/logs /app/.cache && chown -R app:app /app

USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

***REMOVED*** Expose port (using 8004 for ML API)
EXPOSE 8004

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/usr/bin/tini", "--"]

***REMOVED*** Run the application using uvicorn directly with proper worker configuration
***REMOVED*** This bypasses our CLI for production to ensure optimal performance
CMD ["uvicorn", "ml_api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8004", \
     "--workers", "1", \
     "--timeout-keep-alive", "120", \
     "--log-level", "info", \
     "--no-access-log", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--backlog", "1024", \
     "--limit-max-requests", "10000"]