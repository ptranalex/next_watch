# New Developer Onboarding (NextWatch Monorepo)

This guide gets a new developer from **clone → running locally** with the least friction.

## Prerequisites

- Docker Desktop (or Docker Engine) with Docker Compose v2 (`docker compose`)
- Python 3.12+
- [Hatch](https://hatch.pypa.io/latest/)
- Node.js 18+ and pnpm

## Repo layout (high level)

- `apps/`: deployable services (Python, Next.js, Go)
- `libs/`: shared libraries used by services
- `infra/`: Docker Compose, env templates, monitoring, AWS deployment helpers
- `docs/`: cross-cutting documentation (deployment, tracing, Kafka, etc.)

## Local development (recommended)

### 1) Clone and verify tooling

```bash
git clone https://github.com/your-username/next_watch.git
cd next_watch

docker --version
docker compose version
python --version
hatch --version
pnpm --version
```

### 2) Start local dependencies with Docker

NextWatch services expect PostgreSQL + Redis. Recommendation features also use Qdrant.

```bash
# PostgreSQL (dev)
docker run -d --name nextwatch-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=next_watch \
  -p 5432:5432 \
  postgres:16

# Redis (dev)
docker run -d --name nextwatch-redis \
  -p 6379:6379 \
  redis:7

# Qdrant (dev)
docker run -d --name nextwatch-qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest
```

To stop everything later:

```bash
docker rm -f nextwatch-postgres nextwatch-redis nextwatch-qdrant
```

### 3) Configure per-service env files

Most Python services support a local env file in their own directory (recommended for development).

- **Backend API** (`apps/backend-api/.env`):

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=dev-jwt-secret
INTERNAL_API_KEY=dev-internal-api-key
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

- **Auth API** (`apps/auth-api/.env.local`) and **BFF API** (`apps/bff-api/.env.local`) follow the same pattern (see each service README for the exact variable set).

If you prefer a shared dev env template, see `infra/env/development.example`.

### 4) Run the backend services (Hatch)

```bash
# Backend API
cd apps/backend-api
hatch env create
hatch run migrate
hatch run dev
```

In a second terminal:

```bash
# Auth API
cd apps/auth-api
hatch env create
cp .env.example .env
hatch run dev
```

In a third terminal:

```bash
# BFF API
cd apps/bff-api
hatch env create
cp env.example .env
./setup-local-deps.sh
hatch run dev
```

### 5) Run the web app (pnpm)

```bash
cd apps/web-nextjs
pnpm install
pnpm dev
```

### 6) Verify services

- Frontend: `http://localhost:3000`
- BFF API: `http://localhost:8001/health`
- Backend API: `http://localhost:8000/health`
- Auth API: `http://localhost:8003/health`

Interactive docs (where available): `/docs` on each service.

## Production-like stack (Docker Compose)

For production deployment and “all services in containers”, see:

- `infra/DEPLOYMENT.md`
- `docs/deployment/DEPLOYMENT_PRODUCTION.md`
- `infra/compose/prod.yml` (uses `.env.prod`, template: `infra/env/prod.example`)
