# Auth API Optimized Multi-Stage Dockerfile
#
# Build context should be the monorepo root to access local dependencies:
# docker build -f apps/auth-api/Dockerfile -t auth-api .

# Stage 1: Base Python with system dependencies (rarely changes)
FROM python:3.12-alpine AS base

WORKDIR /app

# Install system dependencies with BuildKit cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    curl \
    tini

# Stage 2: Python upgrades (occasionally changes)
FROM base AS python-deps

# Create app user and upgrade pip with cache
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

# Stage 3: Local dependencies (more frequent changes)
FROM python-deps AS local-deps

# Copy and install local dependencies with cache mount
COPY libs/config ./libs/config/
COPY libs/fast-core ./libs/fast-core/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user ./libs/config/ ./libs/fast-core/

# Stage 4: Application dependencies (frequent changes)
FROM local-deps AS app-deps

# Copy and install app dependencies with cache mount
COPY apps/auth-api/pyproject.toml ./pyproject.toml

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -e .

# Stage 5: Application code (most frequent changes)
FROM app-deps AS app-build

# Copy application source code (this layer changes most often)
COPY apps/auth-api/src ./src/

# Final stage: Minimal runtime image
FROM python:3.12-alpine AS final

# Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

# Install runtime dependencies with BuildKit cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache curl tini postgresql-libs

# Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

# Copy Python packages from builder (user installation)
COPY --from=app-build --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --from=app-build --chown=app:app /app/src ./src/

# Create logs directory with write permissions for app user
RUN mkdir -p /app/logs && chown app:app /app/logs && chmod 755 /app/logs

# Ensure app directory has correct ownership
RUN chown -R app:app /app

# Switch to app user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Expose port (following Docker best practice of using 8000 internally)
EXPOSE 8000

# Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

# Run the application using Python module entry point
# This allows the app to use its own settings configuration
# rather than manually passing uvicorn parameters
CMD ["python", "-m", "auth_api"]
