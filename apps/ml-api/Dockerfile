***REMOVED*** Optimized ML API Dockerfile for GitHub Actions
***REMOVED***
***REMOVED*** Build context should be the monorepo root to access local dependencies:
***REMOVED*** docker build -f apps/ml-api/Dockerfile -t ml-api .
***REMOVED***
***REMOVED*** Optimization Strategy:
***REMOVED*** 1. Maximize layer caching by ordering operations by change frequency
***REMOVED*** 2. Use BuildKit cache mounts for package downloads
***REMOVED*** 3. Pre-install heavy dependencies in separate layers
***REMOVED*** 4. Use multi-stage builds to minimize final image size

***REMOVED*** Stage 1: Base Python with system dependencies (changes rarely)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ***REMOVED*** Build optimization
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

***REMOVED*** Install system dependencies (cached layer - changes rarely)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    tini

***REMOVED*** Stage 2: Python dependencies (changes occasionally)
FROM base AS python-deps

***REMOVED*** Create user early for consistent permissions
RUN groupadd -r app && useradd -r -g app app

***REMOVED*** Install pip and setuptools upgrades (cached layer)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel

***REMOVED*** Install PyTorch first (heaviest dependency - cached layer)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user torch==2.7.1+cpu --index-url https://download.pytorch.org/whl/cpu

***REMOVED*** Stage 3: Local dependencies (changes more frequently)
FROM python-deps AS local-deps

***REMOVED*** Copy and install local libraries (these change more often than PyTorch)
COPY libs/cli ./libs/cli/
COPY libs/config ./libs/config/
COPY libs/fast-core ./libs/fast-core/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user ./libs/cli/ ./libs/config/ ./libs/fast-core/

***REMOVED*** Stage 4: App dependencies (changes frequently)
FROM local-deps AS app-deps

***REMOVED*** Copy only pyproject.toml first (dependency specification)
COPY apps/ml-api/pyproject.toml ./pyproject.toml

***REMOVED*** Install app dependencies (but not the app itself yet)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -e . && \
    pip install --user sentence-transformers>=2.2.2 \
    fastapi>=0.104.0 \
    uvicorn>=0.23.2 \
    pydantic>=2.4.2 \
    typer>=0.15.2 \
    rich>=13.7.0 \
    structlog>=23.2.0 \
    python-dotenv>=1.0.0 \
    python-dateutil>=2.9.0 \
    python-multipart>=0.0.20 \
    email-validator>=2.2.0

***REMOVED*** Stage 5: Application code (changes most frequently)
FROM app-deps AS app-build

***REMOVED*** Copy application source code (this layer changes most often)
COPY apps/ml-api/src ./src/

***REMOVED*** Final stage: Runtime image
FROM python:3.12-slim AS final

***REMOVED*** Set essential runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/home/app/.local/bin:$PATH" \
    ***REMOVED*** ML-specific cache directories (required for model storage)
    TORCH_HOME="/app/.cache/torch" \
    TRANSFORMERS_CACHE="/app/.cache/transformers" \
    SENTENCE_TRANSFORMERS_HOME="/app/.cache/sentence_transformers" \
    HF_HUB_CACHE="/app/.cache/huggingface"

WORKDIR /app

***REMOVED*** Install only runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/*

***REMOVED*** Create app user
RUN groupadd -r app && useradd -r -g app app

***REMOVED*** Copy Python packages from builder (all dependencies)
COPY --from=app-build --chown=app:app /root/.local /home/app/.local

***REMOVED*** Copy application code
COPY --from=app-build --chown=app:app /app/src ./src/

***REMOVED*** Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/.cache && chown -R app:app /app

***REMOVED*** Pre-create model cache directory to speed up first run
RUN mkdir -p /app/.cache/torch /app/.cache/transformers /app/.cache/sentence_transformers /app/.cache/huggingface && \
    chown -R app:app /app/.cache

USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

***REMOVED*** Expose port
EXPOSE 8000

***REMOVED*** Use tini for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

***REMOVED*** Run the application using Python module entry point
***REMOVED*** This allows the app to use its own settings configuration
***REMOVED*** rather than manually passing uvicorn parameters
CMD ["python", "-m", "ml_api"]
