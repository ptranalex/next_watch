***REMOVED*** Stage 1: Build dependencies
FROM python:3.9-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

***REMOVED*** Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        python3-dev \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements and shared library
COPY apps/recommendation-api/requirements.txt .
COPY libs/movie-storage /build/movie-storage/

***REMOVED*** Create a requirements file without local paths but keeping ML dependencies
RUN sed 's|file:///.*movie-storage|/build/movie-storage|g' requirements.txt > requirements.docker.txt \
    && pip install --no-cache-dir -r requirements.docker.txt \
    && cd /build/movie-storage \
    && pip install --no-cache-dir -e .

***REMOVED*** Stage 2: Runtime image
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    DISABLE_ML_FEATURES=false

WORKDIR /app

***REMOVED*** Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

***REMOVED*** Copy the application code
COPY apps/recommendation-api/src/recommendation_api /app/recommendation_api/
COPY libs/movie-storage/movie_storage /app/movie_storage/

***REMOVED*** Create an empty .env file to prevent path resolution errors
RUN touch /app/.env

***REMOVED*** Set Python path
ENV PYTHONPATH=/app

EXPOSE 8002

***REMOVED*** Use a non-root user for better security
RUN useradd -m -u 1000 app \
    && mkdir -p /app/logs \
    && chown -R app:app /app

USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "recommendation_api.main:app", "--host", "0.0.0.0", "--port", "8002"] 