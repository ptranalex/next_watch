***REMOVED*** Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

***REMOVED*** Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir hatch && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy movie-storage package from monorepo (excluding .venv and other unnecessary files)
COPY libs/movie-storage/pyproject.toml libs/movie-storage/setup.py* /build/libs/movie-storage/
COPY libs/movie-storage/README.md /build/libs/movie-storage/README.md
COPY libs/movie-storage/movie_storage /build/libs/movie-storage/movie_storage/

***REMOVED*** Install movie-storage package
RUN cd /build/libs/movie-storage && \
    pip install -e .

***REMOVED*** Copy recommendation-api files
COPY apps/recommendation-api/pyproject.toml .
COPY apps/recommendation-api/src ./src

***REMOVED*** Build the wheel package
RUN hatch build -t wheel

***REMOVED*** Stage 2: Runtime
FROM python:3.12-slim

***REMOVED*** Environment variables for runtime optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src" \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT="production" \
    PORT=8002 \
    HOST="0.0.0.0" \
    LOG_LEVEL="info" \
    WORKERS=1 \
    TIMEOUT=120 \
    RELOAD=false \
    PROXY_HEADERS=true \
    FORWARDED_ALLOW_IPS="*" \
    LIMIT_MAX_REQUESTS=10000 \
    BACKLOG=1024

WORKDIR /app

***REMOVED*** Create a non-root user
RUN useradd -m -r recapi

***REMOVED*** Install curl for health checks (and cleanup in the same layer)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy only the necessary movie-storage files (no .venv)
COPY --from=builder /build/libs/movie-storage/movie_storage /app/libs/movie-storage/movie_storage/
COPY --from=builder /build/libs/movie-storage/pyproject.toml /build/libs/movie-storage/setup.py* /app/libs/movie-storage/
COPY --from=builder /build/libs/movie-storage/README.md /app/libs/movie-storage/README.md

***REMOVED*** Copy the source code
COPY apps/recommendation-api/src /app/src

***REMOVED*** Copy the built wheel
COPY --from=builder /build/dist/*.whl .

***REMOVED*** Install dependencies and clean up in the same layer
RUN pip install --no-cache-dir -e /app/libs/movie-storage && \
    pip install --no-cache-dir ./*.whl && \
    rm -f ./*.whl && \
    ***REMOVED*** Remove pip cache and unnecessary files
    find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
        \) -exec rm -rf '{}' + && \
    ***REMOVED*** Remove unnecessary packages
    pip uninstall -y pip wheel setuptools

***REMOVED*** Set file ownership and permissions
RUN chown -R recapi:recapi /app

***REMOVED*** Switch to non-root user
USER recapi

***REMOVED*** Expose the application port
EXPOSE 8002

***REMOVED*** Healthcheck with curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

***REMOVED*** Use tini for proper signal handling and child process reaping
ENTRYPOINT ["/sbin/tini", "--"]

***REMOVED*** Start the application with uvicorn
CMD uvicorn recommendation_api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --timeout-keep-alive ${TIMEOUT} \
    --limit-max-requests ${LIMIT_MAX_REQUESTS} \
    --no-access-log \
    --backlog ${BACKLOG} \
    --reload ${RELOAD} \
    --proxy-headers ${PROXY_HEADERS} \
    --forwarded-allow-ips ${FORWARDED_ALLOW_IPS} 