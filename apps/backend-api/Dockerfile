***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
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
    && curl -sSL https://install.python-poetry.org | python -

***REMOVED*** Copy only dependency-related files first
COPY libs/movie-storage /tmp/movie-storage/
COPY apps/backend-api/pyproject.toml apps/backend-api/poetry.lock* ./
COPY apps/backend-api/src ./src/

***REMOVED*** Fix the local path so `pip install .` works
RUN sed -i 's|movie-storage = {path = "../../libs/movie-storage"}|movie-storage = "*"|g' pyproject.toml

***REMOVED*** Build and install dependencies - combine commands to reduce layers
RUN cd /tmp/movie-storage \
    && poetry build \
    && pip install --no-cache-dir dist/*.whl \
    && cd /app \
    && pip install --no-cache-dir . \
    && rm -rf /tmp/poetry_cache /tmp/movie-storage \
    && apk del .build-deps

***REMOVED*** Stage 2: Runtime image - use a much smaller base
FROM python:3.12-alpine AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install runtime dependencies only
RUN apk add --no-cache libstdc++ curl

***REMOVED*** Copy only what's needed from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/

***REMOVED*** Only copy the application code, not the entire Python installation
COPY apps/backend-api/src ./src/

EXPOSE 8000

***REMOVED*** Use a non-root user for better security
RUN addgroup -S app && adduser -S app -G app
USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"] 