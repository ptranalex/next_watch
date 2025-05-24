FROM python:3.9-slim

***REMOVED*** Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

***REMOVED*** Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Create app user
RUN groupadd -r app && useradd -r -g app app

***REMOVED*** Set work directory
WORKDIR /app

***REMOVED*** Install Poetry
RUN pip install poetry

***REMOVED*** Copy dependency files
COPY pyproject.toml poetry.lock ./

***REMOVED*** Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

***REMOVED*** Copy source code
COPY src/ ./src/

***REMOVED*** Change ownership to app user
RUN chown -R app:app /app
USER app

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health/live || exit 1

***REMOVED*** Expose port
EXPOSE 8001

***REMOVED*** Run the application
CMD ["python", "-m", "bff.cli.main", "serve", "--host", "0.0.0.0", "--port", "8001"] 