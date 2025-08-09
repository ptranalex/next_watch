***REMOVED*** Next Watch Backend API

> FastAPI service for movies, genres, actors, search, and user collections. Includes Fast Core middleware, multi-endpoint health checks, and a robust Typer CLI.

***REMOVED******REMOVED*** 🚀 Quick Start

```bash
***REMOVED*** From repo root
cd apps/backend-api

***REMOVED*** Create environment
hatch env create

***REMOVED*** Configure environment (create .env and set DATABASE_URL, optional REDIS_URL)
${EDITOR:-vi} .env

***REMOVED*** Initialize database schema (Alembic-based)
hatch run migrate

***REMOVED*** Start dev server with auto-reload
hatch run dev
```

API: `http://localhost:8000`

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.12+
- Hatch
- PostgreSQL
- Redis (optional; used by cache tooling and data loaders)

***REMOVED******REMOVED*** 📋 Table of Contents

- Features
- Architecture
- Health Monitoring
- API Reference
- CLI Reference
- Configuration
- Database Setup
- Development
- Docker Deployment

***REMOVED******REMOVED*** ✨ Features

- Movies listing, detail, search, bulk fetch
- Genres listing and detail
- Actors listing, detail, and filmography
- User collections: watchlist, watched, liked (BFF-provided auth via headers)
- Multi-endpoint health checks: `/health`, `/health/live`, `/health/ready`
- Consistent pagination shape: `total, page, per_page, total_pages, has_next, has_prev`

***REMOVED******REMOVED*** 🏗 Architecture

```
src/backend_api/
  core/               ***REMOVED*** Fast Core integration (factory, middleware, metrics)
  config/             ***REMOVED*** Service configuration (shared config library)
  db/                 ***REMOVED*** Engine/session, migrations, operations
  routes/             ***REMOVED*** API v1 routers (movies, genres, actors, search, user collections)
  schemas/            ***REMOVED*** Pydantic models
  services/           ***REMOVED*** Domain services
  cli/                ***REMOVED*** Typer CLI (db, health, cache, serve, config, version)
  main.py             ***REMOVED*** create_app() factory
  __main__.py         ***REMOVED*** Production launcher
```

***REMOVED******REMOVED*** 🏥 Health Monitoring

Endpoints provided via Fast Core health integration:

- `GET /health` – comprehensive
- `GET /health/live` – liveness
- `GET /health/ready` – readiness

Kubernetes probes example:

```yaml
livenessProbe:
  httpGet: { path: /health/live, port: 8000 }
readinessProbe:
  httpGet: { path: /health/ready, port: 8000 }
```

***REMOVED******REMOVED*** 🏗 API Reference

- Movies

  - `GET /api/v1/movies` – list with filters and pagination
  - `GET /api/v1/movies/{movie_id}` – detail
  - `GET /api/v1/movies/top` – top movies by year/genre
  - `GET /api/v1/movies/search` – search by title with filters
  - `GET /api/v1/movies/bulk?ids=1,2,...` – bulk by IDs
  - `GET /api/v1/movies/{movie_id}/cast` – cast list
  - `GET /api/v1/movies/{movie_id}/trailers` – trailers
  - `GET /api/v1/movies/tmdb/{tmdb_id}` – by TMDB ID

- Genres

  - `GET /api/v1/genres` – list
  - `GET /api/v1/genres/{genre_id}` – detail
  - `GET /api/v1/genres/name/{name}` – lookup by name

- Actors

  - `GET /api/v1/actors` – list (popularity, paginated)
  - `GET /api/v1/actors/{actor_id}` – detail
  - `GET /api/v1/actors/{actor_id}/movies` – filmography

- Search

  - `GET /api/v1/search` – placeholder (combined search)
  - `GET /api/v1/search/suggestions` – placeholder
  - `GET /api/v1/search/suggestions/text` – DB-backed basic suggestions

- User collections (BFF-authenticated via `X-User-ID`)
  - `GET /api/v1/user/watchlist`
  - `POST /api/v1/user/watchlist`
  - `DELETE /api/v1/user/watchlist/movies/{movie_id}`
  - `GET /api/v1/user/watched-movies`
  - `POST /api/v1/user/watched-movies`
  - `DELETE /api/v1/user/watched-movies/{movie_id}`
  - `GET /api/v1/user/liked-movies`
  - `POST /api/v1/user/liked-movies`
  - `DELETE /api/v1/user/liked-movies/{movie_id}`
  - `GET /api/v1/user/interactions/movies/{movie_id}`
  - `POST /api/v1/user/interactions/movies/batch`

***REMOVED******REMOVED*** 💻 CLI Reference

Installed console script: `backend-api`

- Top-level commands: `serve`, `config`, `version`
- Groups: `db`, `health`, `cache` (with `redis` subcommands)

Examples:

```bash
***REMOVED*** Show config
backend-api config --verbose

***REMOVED*** Start server (dev recommended: hatch run dev)
python -m backend_api.main

***REMOVED*** DB management
backend-api db init --create-tables
backend-api db migrate
backend-api db downgrade --steps 1
backend-api db teardown --confirm  ***REMOVED*** DEV ONLY

***REMOVED*** Health
backend-api health            ***REMOVED*** same as 'health check'
backend-api health db
backend-api health redis

***REMOVED*** Cache
backend-api cache info -v
backend-api cache keys --pattern "user:*" --limit 50
backend-api cache get "movie:123"
backend-api cache delete "session:456" --confirm
backend-api cache clear --pattern "temp:*" --confirm

***REMOVED*** Cache → Redis suggestion loader
backend-api cache redis populate-suggestions --limit 5000 --no-actors --no-directors
```

Hatch shortcuts (pyproject):

```bash
***REMOVED*** Server
hatch run dev          ***REMOVED*** uvicorn backend_api.main:create_app --factory --reload
hatch run serve        ***REMOVED*** python -m backend_api.main

***REMOVED*** CLI
hatch run cli          ***REMOVED*** python -m backend_api.cli

***REMOVED*** DB
hatch run migrate
hatch run db-init
hatch run db-init-tables
hatch run db-downgrade
hatch run db-teardown

***REMOVED*** Health
hatch run health-check
hatch run health-db
hatch run health-cache

***REMOVED*** Cache
hatch run cache-info
hatch run cache-keys
hatch run cache-get
hatch run cache-clear

***REMOVED*** Tooling
hatch run lint
hatch run format
hatch run test
hatch run test-cov
```

***REMOVED******REMOVED*** ⚙️ Configuration

Powered by the shared `config` library with environment loading and masking.

Core settings:

| Variable       | Description                         | Default                  |
| -------------- | ----------------------------------- | ------------------------ |
| `ENVIRONMENT`  | Environment (`development`, `prod`) | dev                      |
| `PORT`         | HTTP port                           | 8000                     |
| `LOG_LEVEL`    | Log level                           | INFO                     |
| `DEBUG`        | Enable debug mode                   | false                    |
| `DATABASE_URL` | PostgreSQL URL                      | -                        |
| `REDIS_URL`    | Redis URL (optional)                | redis://localhost:6379/0 |
| `CORS_ORIGINS` | CSV of allowed origins              | \*                       |
| `LOGS_DIR`     | Log file directory (optional)       | -                        |

Security and auth-related settings are available via the shared mixins (e.g., JWT), even though auth endpoints are not exposed by this service.

***REMOVED******REMOVED*** 🗄 Database Setup

Typer utilities under `backend_api.scripts.setup_db`:

```bash
***REMOVED*** All-in-one storage setup
python -m backend_api.scripts.setup_db setup-storage

***REMOVED*** Manual flow
python -m backend_api.scripts.setup_db initialize-db
python -m backend_api.scripts.setup_db run-migrations
python -m backend_api.scripts.setup_db check-schema

***REMOVED*** Development profiling
python -m backend_api.scripts.setup_db profile-db --duration 30
```

Note: The app does not auto-create tables. Run migrations before serving.

***REMOVED******REMOVED*** 🛠 Development

```bash
hatch run test
hatch run test-cov
hatch run lint
hatch run format
```

***REMOVED******REMOVED*** 🐳 Docker

```bash
docker build -f apps/backend-api/Dockerfile -t backend-api .
docker run -p 8000:8000 --env-file .env backend-api
```

Production checklist:

- `ENVIRONMENT=production`, `DEBUG=false`
- Set strong secrets (e.g., JWT)
- Run `run-migrations`
- Configure probes to `/health/live` and `/health/ready`

***REMOVED******REMOVED*** 📚 More Docs

- `src/backend_api/cli/README.md` – CLI details
- `src/backend_api/core/README.md` – App factory and middleware
- `src/backend_api/routes/README.md` – Route docs
- `src/backend_api/services/README.md` – Services overview

---

Next Watch Backend API focuses on reliable movie data and user collections with consistent responses and strong operational tooling.
