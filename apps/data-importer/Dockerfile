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

***REMOVED*** Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

***REMOVED*** Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

***REMOVED*** Copy the movie-storage library
COPY libs/movie-storage /tmp/movie-storage/

***REMOVED*** Install movie-storage
RUN cd /tmp/movie-storage && \
    poetry build && \
    pip install dist/*.whl && \
    cd /app

***REMOVED*** Copy necessary files for installation
COPY apps/data-importer/pyproject.toml ./
COPY apps/data-importer/README.md ./
COPY apps/data-importer/src ./src/

***REMOVED*** Fix the movie-storage dependency
RUN sed -i 's|movie-storage = {path = "../../libs/movie-storage", develop = true}|movie-storage = "*"|g' pyproject.toml

***REMOVED*** Install dependencies directly with pip
RUN pip install . && \
    rm -rf /tmp/poetry_cache

***REMOVED*** Copy the rest of the application code
COPY apps/data-importer/data ./data/

***REMOVED*** Command to run the importer CLI
***REMOVED*** The main entry point is in data_importer.cli:main
CMD ["python", "-m", "data_importer"] 