***REMOVED*** Use Python 3.11 slim image
FROM python:3.11-slim

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Install Poetry
RUN pip install poetry

***REMOVED*** Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

***REMOVED*** Copy Poetry files
COPY pyproject.toml poetry.lock ./

***REMOVED*** Install dependencies
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

***REMOVED*** Copy source code
COPY . .

***REMOVED*** Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

***REMOVED*** Expose port
EXPOSE 8003

***REMOVED*** Command to run the application
CMD ["poetry", "run", "uvicorn", "src.auth_api.main:app", "--host", "0.0.0.0", "--port", "8003"] 