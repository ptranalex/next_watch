***REMOVED*** Stage 1: Build dependencies and package
FROM python:3.9-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

***REMOVED*** Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

***REMOVED*** Copy movie-storage dependency to expected location
COPY libs/movie-storage ./libs/movie-storage

***REMOVED*** First, install movie-storage dependency
RUN cd libs/movie-storage && pip install --no-cache-dir --user .

***REMOVED*** Copy requirements.txt (pre-generated without movie-storage)
COPY apps/auth-api/requirements.txt ./

***REMOVED*** Install other dependencies to user directory
RUN pip install --no-cache-dir --user -r requirements.txt

***REMOVED*** Copy application code and config
COPY apps/auth-api/src ./src/
COPY apps/auth-api/pyproject.toml ./

***REMOVED*** Fix the movie-storage path in pyproject.toml for Docker build context
RUN sed -i 's|path = "../../libs/movie-storage"|path = "./libs/movie-storage"|' pyproject.toml

***REMOVED*** Install the current project to user directory
RUN pip install --no-cache-dir --user -e .

***REMOVED*** Stage 2: Runtime image
FROM python:3.9-alpine AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install runtime dependencies
RUN apk add --no-cache \
    curl \
    postgresql-libs

***REMOVED*** Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

***REMOVED*** Copy Python packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=builder --chown=app:app /app/src ./src/

***REMOVED*** Create logs directory
RUN mkdir -p /app/logs && chown -R app:app /app

USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

***REMOVED*** Expose port
EXPOSE 8003

***REMOVED*** Run the application
CMD ["python", "-m", "auth_api.cli.main", "serve", "--host", "0.0.0.0", "--port", "8003"] 