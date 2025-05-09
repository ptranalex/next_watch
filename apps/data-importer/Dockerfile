ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

***REMOVED*** Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

***REMOVED*** Install system dependencies and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && curl -sSL https://install.python-poetry.org | python - \
 && apt-get purge -y curl \
 && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy and build the shared movie-storage library
COPY libs/movie-storage /tmp/movie-storage/
RUN cd /tmp/movie-storage && \
    poetry build && \
    pip install dist/*.whl

***REMOVED*** Copy app source files and patch pyproject.toml
COPY apps/data-importer/pyproject.toml apps/data-importer/README.md ./
COPY apps/data-importer/src ./src/
RUN sed -i 's|movie-storage = {path = "../../libs/movie-storage", develop = true}|movie-storage = "*"|g' pyproject.toml \
 && pip install . \
 && rm -rf /tmp/poetry_cache

***REMOVED*** Create data directory
RUN mkdir -p /app/data/

CMD ["python", "-m", "data_importer"]