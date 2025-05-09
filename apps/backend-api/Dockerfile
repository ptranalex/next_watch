ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

***REMOVED*** Set up environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

***REMOVED*** Install system dependencies with retry logic and alternate mirrors
RUN set -eux; \
    apt-get update || (sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && apt-get update); \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

***REMOVED*** Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

***REMOVED*** Copy dependency-related files first
COPY libs/movie-storage /tmp/movie-storage/
COPY apps/backend-api/pyproject.toml ./
COPY apps/backend-api/README.md ./
COPY apps/backend-api/src ./src/ 

***REMOVED*** Now install movie-storage and backend-api dependencies
RUN cd /tmp/movie-storage && \
    poetry build && \
    pip install dist/*.whl && \
    cd /app && \
    sed -i 's|movie-storage = {path = "../../libs/movie-storage"}|movie-storage = "*"|g' pyproject.toml && \
    pip install . && \
    rm -rf /tmp/poetry_cache

***REMOVED*** Now copy the rest of the app source (won’t invalidate earlier layers unless code changes)
COPY apps/backend-api/src ./src/

***REMOVED*** Copy the rest of the application code
COPY apps/backend-api/src ./src/

***REMOVED*** Create tests directory
RUN mkdir -p ./tests/

***REMOVED*** Expose the port the app runs on
EXPOSE 8000

***REMOVED*** Run the application
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"] 