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
    SENTENCE_TRANSFORMERS_HOME="/app/.cache/sentence_transformers"

WORKDIR /app

***REMOVED*** Create a non-root user
RUN useradd -m -r mlapi

***REMOVED*** Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
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

***REMOVED*** Expose the application port
EXPOSE 8004

***REMOVED*** Healthcheck with curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

***REMOVED*** Start the application
CMD ["python", "-m", "ml_api.app"]