# Optimized BFF API Dockerfile for fast builds
#
# Build context should be the monorepo root to access local dependencies:
# docker build -f apps/bff-api/Dockerfile -t bff-api .
#
# Optimization Strategy:
# 1. Maximize layer caching by ordering operations by change frequency
# 2. Use BuildKit cache mounts for package downloads
# 3. Separate dependency installation from app code for better caching
# 4. Use multi-stage builds to minimize final image size

# Stage 1: Base Python with system dependencies (changes rarely)
FROM python:3.12-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Build optimization
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies with cache mounts (cached layer - changes rarely)
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    curl \
    tini

# Stage 2: Python dependencies (changes occasionally)
FROM base AS python-deps

# Create user early for consistent permissions
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

# Install pip and setuptools upgrades (cached layer)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

# Stage 3: Local dependencies (changes more frequently than base deps)
FROM python-deps AS local-deps

# Copy and install local libraries (order by change frequency)
COPY libs/fast-core ./libs/fast-core/
COPY libs/config ./libs/config/
COPY libs/cache ./libs/cache/
COPY libs/cli ./libs/cli/

# Install local dependencies with cache mount
# Install as regular packages (not editable) to avoid path issues in multi-stage builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user ./libs/config/ && \
    pip install --user ./libs/cache/ && \
    pip install --user ./libs/cli/ && \
    pip install --user ./libs/fast-core/

# Stage 4: App dependencies (changes frequently)
FROM local-deps AS app-deps

# Copy only pyproject.toml first (dependency specification)
COPY apps/bff-api/pyproject.toml ./pyproject.toml

# Install app dependencies with cache mount (but not the app itself yet)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user .

# Stage 5: Application code (changes most frequently)
FROM app-deps AS app-build

# Copy application source code (this layer changes most often)
COPY apps/bff-api/src ./src/

# Final stage: Minimal runtime image
FROM python:3.12-alpine AS final

# Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH" \
    PYTHONUSERBASE=/home/app/.local

WORKDIR /app

# Install only runtime dependencies with cache mount
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add --no-cache curl tini cronie

# Create app user
RUN addgroup -g 1000 app && adduser -u 1000 -G app -s /bin/sh -D app

# Copy Python packages from builder (all dependencies)
COPY --from=app-build --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --from=app-build --chown=app:app /app/src ./src/

# Copy startup scripts
COPY --chown=app:app apps/bff-api/scripts/ ./scripts/

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R app:app /app

# Fix cron permissions for non-root user
RUN mkdir -p /var/run && touch /var/run/crond.pid && chown app:app /var/run/crond.pid

# Note: Keep as root for cron daemon, but startup script switches to app user for the API

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
CMD ["python", "-m", "bff_api"]
