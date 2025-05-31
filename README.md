***REMOVED*** Next Watch

A comprehensive movie discovery and tracking platform built with modern microservices architecture.

***REMOVED******REMOVED*** 🏗️ Architecture

Next Watch consists of 5 main services:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   BFF API   │───▶│  Auth API   │    │ Backend API │
│  (Next.js)  │    │ (Port 8001) │    │ (Port 8003) │    │ (Port 8000) │
│ (Port 3000) │    └─────────────┘    └─────────────┘    └─────────────┘
└─────────────┘           │                   │                   │
                          │                   │                   │
                          ▼                   ▼                   ▼
                    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                    │    Redis    │    │ PostgreSQL  │    │Data Importer│
                    │(Host:6379)  │    │(Host:5432)  │    │ (On-demand) │
                    └─────────────┘    └─────────────┘    └─────────────┘
```

***REMOVED******REMOVED******REMOVED*** Services

- **Frontend** (`apps/web-nextjs`): Next.js 15 web application
- **BFF API** (`apps/bff-api`): Backend for Frontend aggregation layer
- **Auth API** (`apps/auth-api`): Dedicated authentication service
- **Backend API** (`apps/backend-api`): Core business logic and data access
- **Data Importer** (`apps/data-importer`): Movie data synchronization service

***REMOVED******REMOVED******REMOVED*** Shared Libraries

- **Movie Storage** (`libs/movie-storage`): Shared data models and database utilities

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Docker & Docker Compose
- PostgreSQL (running on host)
- Redis (running on host)

***REMOVED******REMOVED******REMOVED*** Local Development

```bash
***REMOVED*** Clone the repository
git clone https://github.com/your-username/next_watch.git
cd next_watch

***REMOVED*** Copy environment template
cp infra/env.prod.example .env.prod

***REMOVED*** Edit environment variables
nano .env.prod

***REMOVED*** Build all services
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest .
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest .
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest .
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest .
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest .

***REMOVED*** Start services
docker-compose -f infra/docker-compose.prod.yml --env-file .env.prod up -d

***REMOVED*** Check status
docker ps
```

***REMOVED******REMOVED******REMOVED*** Using the Deployment Script

```bash
***REMOVED*** Make executable
chmod +x scripts/deploy-prod.sh

***REMOVED*** Deploy all services
./scripts/deploy-prod.sh

***REMOVED*** Deploy with data import
./scripts/deploy-prod.sh --import

***REMOVED*** Build only (no deployment)
./scripts/deploy-prod.sh --build-only
```

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Required Environment Variables

```bash
***REMOVED*** Docker Images
DOCKER_BACKEND_IMAGE=next-watch-backend:latest
DOCKER_AUTH_IMAGE=next-watch-auth:latest
DOCKER_BFF_IMAGE=next-watch-bff:latest
DOCKER_FRONTEND_IMAGE=next-watch-frontend:latest
DOCKER_IMPORTER_IMAGE=next-watch-importer:latest

***REMOVED*** Database
POSTGRES_USER=next_watch_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=next_watch

***REMOVED*** Security
JWT_SECRET=your-super-secure-jwt-secret
INTERNAL_API_KEY=your-internal-api-key

***REMOVED*** External APIs
TMDB_ACCESS_TOKEN=your-tmdb-token
OMDB_API_KEY=your-omdb-key
```

See `infra/env.prod.example` for complete configuration options.

***REMOVED******REMOVED*** 🔄 CI/CD Workflows

***REMOVED******REMOVED******REMOVED*** GitHub Actions

The project includes comprehensive GitHub Actions workflows:

***REMOVED******REMOVED******REMOVED******REMOVED*** **Build Workflow** (`.github/workflows/build.yml`)

- Builds all 5 services when their code changes
- Supports building shared libraries (`libs/movie-storage`)
- Pushes images to GitHub Container Registry
- Supports manual builds with `build_all` option

***REMOVED******REMOVED******REMOVED******REMOVED*** **Deploy Workflow** (`.github/workflows/deploy.yml`)

- Deploys services to production server
- Uses Docker Compose with proper environment configuration
- Supports selective deployment of individual services
- Includes health checks and cleanup

***REMOVED******REMOVED******REMOVED******REMOVED*** **Release Workflow** (`.github/workflows/release.yml`)

- Automatically builds and deploys on `main` branch pushes
- Detects changes in each service
- Orchestrates build → deploy pipeline
- Supports manual releases with custom service selection

***REMOVED******REMOVED******REMOVED*** Workflow Triggers

**Automatic (on push to main):**

- Detects changes in each service directory
- Builds only changed services
- Deploys changed services automatically

**Manual (workflow_dispatch):**

- Build all services regardless of changes
- Deploy specific services
- Full stack deployment

***REMOVED******REMOVED******REMOVED*** Required Secrets

Configure these in your GitHub repository settings:

```bash
***REMOVED*** Deployment
DEPLOY_KEY          ***REMOVED*** SSH private key for server access
DEPLOY_HOST         ***REMOVED*** Server hostname/IP
DEPLOY_USER         ***REMOVED*** SSH username
GH_PAT             ***REMOVED*** GitHub Personal Access Token

***REMOVED*** Database
POSTGRES_USER       ***REMOVED*** Database username
POSTGRES_PASSWORD   ***REMOVED*** Database password
POSTGRES_DB         ***REMOVED*** Database name

***REMOVED*** Security
JWT_SECRET          ***REMOVED*** JWT signing secret
INTERNAL_API_KEY    ***REMOVED*** Service-to-service API key

***REMOVED*** External APIs (optional)
TMDB_ACCESS_TOKEN   ***REMOVED*** The Movie Database API token
OMDB_API_KEY        ***REMOVED*** Open Movie Database API key
```

***REMOVED******REMOVED*** 📊 Service Health Checks

All services include comprehensive health checks:

- **Backend API**: `GET /health`
- **Auth API**: `GET /health`
- **BFF API**: `GET /health`
- **Frontend**: Process-based health check
- **Data Importer**: On-demand service

Health checks include:

- Service availability
- Database connectivity
- Dependency verification
- Resource monitoring

***REMOVED******REMOVED*** 🛠️ Development

***REMOVED******REMOVED******REMOVED*** Individual Service Development

Each service can be developed independently:

```bash
***REMOVED*** Backend API
cd apps/backend-api
poetry install
poetry run backend-api serve --reload

***REMOVED*** Auth API
cd apps/auth-api
poetry install
poetry run auth-api serve --reload

***REMOVED*** BFF API
cd apps/bff-api
poetry install
poetry run bff-api serve --reload

***REMOVED*** Frontend
cd apps/web-nextjs
pnpm install
pnpm dev

***REMOVED*** Data Importer
cd apps/data-importer
poetry install
poetry run data-importer sync
```

***REMOVED******REMOVED******REMOVED*** CLI Tools

Each Python service includes comprehensive CLI tools:

```bash
***REMOVED*** Backend API
backend-api --help
backend-api serve --reload --verbose
backend-api health check

***REMOVED*** Auth API
auth-api --help
auth-api serve --reload --verbose
auth-api users list
auth-api health check

***REMOVED*** BFF API
bff-api --help
bff-api serve --reload --verbose
bff-api cache info

***REMOVED*** Data Importer
data-importer --help
data-importer sync --verbose
data-importer import movies
```

***REMOVED******REMOVED*** 📚 Documentation

- **Deployment Guide**: `DEPLOYMENT.md`
- **API Documentation**: Available at `/docs` on each service
- **Architecture Decisions**: `docs/` directory
- **Service READMEs**: Each service has detailed documentation

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes to relevant services
4. Test locally with Docker Compose
5. Submit a pull request

The CI/CD pipeline will automatically:

- Build changed services
- Run tests
- Deploy to staging (if configured)

***REMOVED******REMOVED*** 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
