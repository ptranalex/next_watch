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

***REMOVED*** Build the wheel package
RUN hatch build -t wheel

***REMOVED*** Stage 2: Runtime
FROM python:3.12-slim

***REMOVED*** Environment variables for runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

WORKDIR /app

***REMOVED*** Create a non-root user
RUN useradd -m -r mlapi

***REMOVED*** Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy and install the built wheel only
COPY --from=builder /build/dist/*.whl .
RUN pip install --no-cache-dir ./*.whl && rm -f ./*.whl

***REMOVED*** Set file ownership and permissions
RUN chown -R mlapi:mlapi /app

***REMOVED*** Switch to non-root user
USER mlapi

***REMOVED*** Expose the application port
EXPOSE 8004

***REMOVED*** Healthcheck with curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

***REMOVED*** Start the application
CMD ["python", "-m", "ml_api.app"]