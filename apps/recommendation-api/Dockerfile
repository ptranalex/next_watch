***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.9-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gcc \
        python3-dev \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements and source code
COPY apps/recommendation-api/requirements.txt .
COPY apps/recommendation-api/pyproject.toml .
COPY apps/recommendation-api/README.md .
COPY apps/recommendation-api/src ./src/
COPY libs/movie-storage /tmp/movie-storage/

***REMOVED*** Create a temporary requirements file without the local dependency
RUN sed '/file:\/\/.*movie-storage/d' requirements.txt > requirements.docker.txt

***REMOVED*** Fix the movie-storage path in pyproject.toml
RUN sed -i 's|{path = "../../libs/movie-storage"}|{path = "/tmp/movie-storage"}|g' pyproject.toml

***REMOVED*** Install dependencies
RUN pip install --no-cache-dir -r requirements.docker.txt \
    && cd /tmp/movie-storage \
    && pip install --no-cache-dir -e . \
    && cd /app \
    && pip install --no-cache-dir -e . \
    && rm -rf /tmp/movie-storage requirements.docker.txt

***REMOVED*** Stage 2: Runtime image
FROM python:3.9-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install runtime dependencies only
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy only what's needed from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

***REMOVED*** Only copy the application code
COPY apps/recommendation-api/src ./src/

EXPOSE 8002

***REMOVED*** Use a non-root user for better security
RUN useradd -m -u 1000 app

***REMOVED*** Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app

USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "recommendation_api.main:app", "--host", "0.0.0.0", "--port", "8002"] 