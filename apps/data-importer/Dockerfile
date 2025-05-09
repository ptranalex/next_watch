***REMOVED*** Stage 1: Build dependencies and package
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-alpine AS builder

***REMOVED*** Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install build dependencies in a single layer
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    curl \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && curl -sSL https://install.python-poetry.org | python -

***REMOVED*** Copy and build the shared movie-storage library
COPY libs/movie-storage /tmp/movie-storage/
COPY apps/data-importer/pyproject.toml apps/data-importer/poetry.lock* ./
COPY apps/data-importer/src ./src/

***REMOVED*** Build and install dependencies
RUN cd /tmp/movie-storage \
    && poetry build \
    && pip install --no-cache-dir dist/*.whl \
    && sed -i 's|movie-storage = {path = "../../libs/movie-storage", develop = true}|movie-storage = "*"|g' pyproject.toml \
    && pip install --no-cache-dir . \
    && rm -rf /tmp/movie-storage /tmp/poetry_cache \
    && apk del .build-deps

***REMOVED*** Stage 2: Runtime image
FROM python:${PYTHON_VERSION}-alpine AS final

***REMOVED*** Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install runtime dependencies only
RUN apk add --no-cache libstdc++

***REMOVED*** Copy only what's needed from builder - use find to determine the correct path
RUN mkdir -p /usr/local/lib/python3.12/site-packages

***REMOVED*** Copy only what's needed from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/python /usr/local/bin/

***REMOVED*** Copy application code
COPY apps/data-importer/src ./src/

***REMOVED*** Create data directory with proper permissions
RUN mkdir -p /app/data/

***REMOVED*** Create non-root user for better security
RUN addgroup -S app && adduser -S app -G app \
    && chown -R app:app /app/data/

***REMOVED*** Switch to non-root user
USER app

CMD ["python", "-m", "data_importer"]