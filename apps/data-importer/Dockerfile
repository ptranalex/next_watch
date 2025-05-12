***REMOVED*** Stage 1: Build dependencies
FROM python:3.12-slim-bullseye AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

***REMOVED*** Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Create virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

***REMOVED*** Install Python dependencies
COPY apps/data-importer/requirements.txt .
***REMOVED*** Remove lines containing absolute file paths
RUN grep -v "file:" requirements.txt > filtered_requirements.txt && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r filtered_requirements.txt

***REMOVED*** Copy and install local packages
COPY libs/movie-storage ./movie-storage
RUN pip install --no-cache-dir ./movie-storage

***REMOVED*** Copy application code
COPY apps/data-importer/src ./src

***REMOVED*** Aggressive clean up to reduce image size
RUN find /venv -name "*.pyc" -delete && \
    find /venv -name "__pycache__" -delete && \
    find /venv -name "*.dist-info" -exec rm -rf {} +; true && \
    find /venv -name "*.egg-info" -exec rm -rf {} +; true && \
    find /venv -name "tests" -type d -exec rm -rf {} +; true && \
    find /venv -name "*.so" -exec strip {} \; || true && \
    find /venv -name "*.c" -delete && \
    find /venv -name "*.pyx" -delete && \
    find /venv -name "*.txt" -delete && \
    find /venv -path "*/doc/*" -delete && \
    find /venv -path "*/docs/*" -delete && \
    find /venv -path "*/examples/*" -delete

***REMOVED*** Stage 2: Runtime image - uses slim-bullseye for smaller size
FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    PYTHONPATH=/app:/app/src

WORKDIR /app

***REMOVED*** Runtime dependencies only - minimal install
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy virtual env from builder
COPY --from=builder /venv /venv

***REMOVED*** Copy application code
COPY --from=builder /build/src ./src

***REMOVED*** Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs

***REMOVED*** Create a non-root user
RUN groupadd -r app && useradd -r -g app app && \
    chown -R app:app /app
USER app

***REMOVED*** Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import data_importer; assert data_importer.__version__"

***REMOVED*** Default command
ENTRYPOINT ["python", "-m", "data_importer"]
CMD ["sync", "movies", "--help"]