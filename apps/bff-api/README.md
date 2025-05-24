***REMOVED*** BFF (Backend for Frontend) Service

The BFF serves as a middle layer between the Next.js frontend and backend services, providing screen-specific, UI-ready data payloads and hiding service boundaries from the frontend.

***REMOVED******REMOVED*** 🎯 Purpose

The BFF aggregates data from multiple backend services and provides optimized endpoints for specific UI screens, reducing the complexity and number of API calls required by the frontend.

***REMOVED******REMOVED*** 🧱 Core Responsibilities

- ✅ **Data Aggregation**: Combine data from backend-api, databases, and other services
- ✅ **Screen-Oriented Endpoints**: Provide UI-specific endpoints like `/bff/home`, `/bff/movies/:id`
- ✅ **User-Aware Logic**: Embed user-specific data (watchlist status, favorites, ratings)
- ✅ **Service Abstraction**: Hide backend service boundaries from the frontend
- ✅ **Caching & Performance**: Optimize data delivery with intelligent caching

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.9+
- Poetry (for dependency management)
- Redis (for caching)
- Backend API service running

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Navigate to BFF directory
cd apps/bff

***REMOVED*** Install dependencies
poetry install

***REMOVED*** Set up environment variables
cp .env.example .env
***REMOVED*** Edit .env with your configuration
```

***REMOVED******REMOVED******REMOVED*** Running the Service

```bash
***REMOVED*** Development mode with auto-reload
poetry run bff serve --reload --verbose

***REMOVED*** Production mode
poetry run bff serve --host 0.0.0.0 --port 8001

***REMOVED*** Check configuration
poetry run bff config

***REMOVED*** Health check
poetry run bff health-check
```

***REMOVED******REMOVED*** 📡 API Endpoints

***REMOVED******REMOVED******REMOVED*** Screen-Oriented Endpoints

***REMOVED******REMOVED******REMOVED******REMOVED*** Home Screen

```http
GET /bff/home?user_id=123
```

Returns aggregated data for the home screen:

- Featured movies
- Popular movies
- Recent releases
- User recommendations (if user_id provided)
- Available genres

***REMOVED******REMOVED******REMOVED******REMOVED*** Movie Detail Screen

```http
GET /bff/movies/123?user_id=456
```

Returns complete movie detail data:

- Movie metadata
- Cast information
- Similar movies
- User interactions (watchlist, favorites, ratings)

***REMOVED******REMOVED******REMOVED******REMOVED*** Genre Screen

```http
GET /bff/genres/1?page=1&limit=20&user_id=123
```

Returns genre-specific movie listings with pagination.

***REMOVED******REMOVED******REMOVED******REMOVED*** Search Screen

```http
GET /bff/search?q=action&page=1&limit=20&user_id=123
```

Returns search results with user-specific data.

***REMOVED******REMOVED******REMOVED*** Health Endpoints

```http
GET /health/          ***REMOVED*** Basic health check
GET /health/ready     ***REMOVED*** Readiness check (K8s)
GET /health/live      ***REMOVED*** Liveness check (K8s)
```

***REMOVED******REMOVED*** 🧩 Integration Points

***REMOVED******REMOVED******REMOVED*** Backend Services

- **backend-api**: Primary source for movie metadata, genres, cast
- **user-interaction**: Watchlist, favorites, ratings (can be part of backend-api)
- **Redis**: Caching layer for performance optimization

***REMOVED******REMOVED******REMOVED*** Configuration

Environment variables:

```bash
***REMOVED*** Server Configuration
HOST=0.0.0.0
PORT=8001
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

***REMOVED*** Backend Integration
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30

***REMOVED*** Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

***REMOVED*** Security
JWT_SECRET=your-jwt-secret-here
```

***REMOVED******REMOVED*** 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   BFF Service   │────│  Backend API    │
│                 │    │                 │    │                 │
│ - Home Screen   │    │ - Data Agg.     │    │ - Movie Data    │
│ - Movie Detail  │    │ - User Context  │    │ - User Data     │
│ - Search        │    │ - Caching       │    │ - Business Logic│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Caching)     │
                       └─────────────────┘
```

***REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Run all tests
poetry run pytest

***REMOVED*** Run with coverage
poetry run pytest --cov=bff

***REMOVED*** Run specific test file
poetry run pytest tests/test_routes.py

***REMOVED*** Run with verbose output
poetry run pytest -v
```

***REMOVED******REMOVED*** 🔧 Development

***REMOVED******REMOVED******REMOVED*** Code Style

The project follows Google Python Style Guide:

```bash
***REMOVED*** Format code
poetry run black src/ tests/

***REMOVED*** Sort imports
poetry run isort src/ tests/

***REMOVED*** Lint code
poetry run flake8 src/ tests/

***REMOVED*** Type checking
poetry run mypy src/
```

***REMOVED******REMOVED******REMOVED*** Adding New Endpoints

1. **Define the endpoint** in `src/bff/routes/bff.py`
2. **Add Pydantic models** for request/response validation
3. **Implement backend client methods** if needed
4. **Write tests** in `tests/test_routes.py`
5. **Update documentation**

***REMOVED******REMOVED******REMOVED*** Project Structure

```
apps/bff/
├── src/bff/
│   ├── config/          ***REMOVED*** Configuration management
│   ├── routes/          ***REMOVED*** FastAPI route handlers
│   ├── services/        ***REMOVED*** External service clients
│   ├── middlewares/     ***REMOVED*** Custom middleware
│   ├── cli/            ***REMOVED*** Command-line interface
│   └── main.py         ***REMOVED*** FastAPI application
├── tests/              ***REMOVED*** Test suite
├── pyproject.toml      ***REMOVED*** Dependencies and config
└── README.md          ***REMOVED*** This file
```

***REMOVED******REMOVED*** 🚀 Deployment

***REMOVED******REMOVED******REMOVED*** Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src/ ./src/
CMD ["poetry", "run", "bff", "serve"]
```

***REMOVED******REMOVED******REMOVED*** Environment Variables

Ensure these are set in production:

- `ENVIRONMENT=production`
- `JWT_SECRET` (secure random string)
- `BACKEND_API_URL` (production backend URL)
- `REDIS_URL` (production Redis instance)

***REMOVED******REMOVED*** 📊 Monitoring

The BFF service provides several monitoring endpoints:

- Health checks for load balancer integration
- Structured logging for observability
- Request/response timing middleware
- Error tracking and reporting

***REMOVED******REMOVED*** 🤝 Contributing

1. Follow TDD practices - write tests first
2. Use type hints for all functions
3. Add docstrings following Google style
4. Update README for any API changes
5. Ensure all tests pass before submitting

***REMOVED******REMOVED*** 📝 License

This project is part of the Next Watch movie platform.
