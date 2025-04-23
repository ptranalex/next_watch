FROM python:3.9-slim

WORKDIR /app

***REMOVED*** Install Poetry
RUN pip install poetry==1.5.1

***REMOVED*** Copy project files
COPY pyproject.toml poetry.lock* ./

***REMOVED*** Configure Poetry to not use virtualenvs in Docker
RUN poetry config virtualenvs.create false

***REMOVED*** Install dependencies only (this is done separately to leverage Docker caching)
RUN poetry install --no-dev --no-interaction --no-ansi

***REMOVED*** Copy the rest of the application
COPY . .

***REMOVED*** Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

***REMOVED*** Expose the port
EXPOSE 8000

***REMOVED*** Run the application
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"] 