***REMOVED*** This Dockerfile is used to build the data-importer package.


***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
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
    postgresql-dev \
    && pip install --no-cache-dir hatch

***REMOVED*** Copy only dependency-related files first
COPY libs/movie-storage /tmp/movie-storage/
COPY apps/data-importer/pyproject.toml ./pyproject.toml.orig

***REMOVED*** Install the movie-storage package first
WORKDIR /tmp/movie-storage
RUN pip install -e .

***REMOVED*** Return to app directory and install application
WORKDIR /app
COPY apps/data-importer/src ./src/

***REMOVED*** Create a modified pyproject.toml without the local dependency since we install movie-storage separately
RUN sed '/movie-storage @ file/d' pyproject.toml.orig > pyproject.toml

***REMOVED*** Install the application using hatch
RUN pip install --no-cache-dir -e .

***REMOVED*** Stage 2: Runtime image - use a much smaller base
FROM python:3.12-alpine AS final

***REMOVED*** Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src \
    ENVIRONMENT="production" \
    LOG_LEVEL="info"

WORKDIR /app

***REMOVED*** Install runtime dependencies
RUN apk add --no-cache libstdc++ curl postgresql-client tini

***REMOVED*** Copy the installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/data-importer /usr/local/bin/

***REMOVED*** Copy the movie-storage package
COPY --from=builder /tmp/movie-storage /app/movie-storage
RUN pip install -e /app/movie-storage

***REMOVED*** Only copy the application code
COPY apps/data-importer/src ./src/

***REMOVED*** Use a non-root user for better security
RUN addgroup -S app && adduser -S app -G app

***REMOVED*** Create logs and data directories with proper permissions
RUN mkdir -p /app/logs /app/data && chown -R app:app /app

USER app

***REMOVED*** Add health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD data-importer --help || exit 1

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Default command - use the installed CLI
CMD ["data-importer", "sync", "movies", "--help"] 