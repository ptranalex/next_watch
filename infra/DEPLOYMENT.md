***REMOVED*** Next Watch Production Deployment Guide

This guide covers deploying the complete Next Watch application stack using Docker Compose.

***REMOVED******REMOVED*** 🏗️ Architecture Overview

The production deployment includes these services:

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

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Prerequisites

Ensure you have the following installed:

- Docker (20.10+)
- Docker Compose (2.0+)
- PostgreSQL (running on host)
- Redis (running on host)

***REMOVED******REMOVED******REMOVED*** 2. Environment Setup

```bash
***REMOVED*** Copy the environment template
cp infra/env/prod.example .env.prod

***REMOVED*** Edit the environment file with your values
nano .env.prod
```

***REMOVED******REMOVED******REMOVED*** 3. Build and Deploy

```bash
***REMOVED*** Make the deployment script executable
chmod +x scripts/deploy-prod.sh

***REMOVED*** Run the complete deployment
./scripts/deploy-prod.sh

***REMOVED*** Or build and deploy with data import
./scripts/deploy-prod.sh --import
```

***REMOVED******REMOVED*** 📋 Individual Docker Build Commands

***REMOVED******REMOVED******REMOVED*** Build All Services

```bash
***REMOVED*** Backend API
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest .

***REMOVED*** Auth API
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest .

***REMOVED*** BFF API
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest .

***REMOVED*** Frontend
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest .

***REMOVED*** Data Importer
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest .
```

***REMOVED******REMOVED******REMOVED*** Build All in Parallel

```bash
***REMOVED*** Build all services simultaneously for faster builds
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest . &
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest . &
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest . &
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest . &
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest . &
wait
echo "✅ All builds completed"
```

***REMOVED******REMOVED*** 🐳 Docker Compose Commands

***REMOVED******REMOVED******REMOVED*** Basic Operations

```bash
***REMOVED*** Start all services
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

***REMOVED*** Stop all services
docker compose -f infra/compose/prod.yml --env-file .env.prod down

***REMOVED*** View service status
docker compose -f infra/compose/prod.yml --env-file .env.prod ps

***REMOVED*** View logs for all services
docker compose -f infra/compose/prod.yml --env-file .env.prod logs -f

***REMOVED*** View logs for specific service
docker compose -f infra/compose/prod.yml --env-file .env.prod logs -f backend-api
```

***REMOVED******REMOVED******REMOVED*** Service Management

```bash
***REMOVED*** Restart a specific service
docker compose -f infra/compose/prod.yml --env-file .env.prod restart backend-api

***REMOVED*** Scale a service (if needed)
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d --scale bff-api=2

***REMOVED*** Update a single service
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d --no-deps backend-api
```

***REMOVED******REMOVED******REMOVED*** Data Import

```bash
***REMOVED*** Run data import (one-time)
docker compose -f infra/compose/prod.yml --env-file .env.prod --profile import up data-importer

***REMOVED*** Run data sync (scheduled)
docker compose -f infra/compose/prod.yml --env-file .env.prod --profile sync up data-importer
```

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Required Environment Variables

Create `.env.prod` with these essential variables:

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
JWT_SECRET=your-super-secure-jwt-secret-key
INTERNAL_API_KEY=your-internal-api-key

***REMOVED*** External APIs
TMDB_ACCESS_TOKEN=your-tmdb-token
OMDB_API_KEY=your-omdb-key
```

***REMOVED******REMOVED******REMOVED*** Service Dependencies

The services start in this order due to health check dependencies:

1. **Backend API** (core service)
2. **Auth API** (authentication)
3. **BFF API** (depends on Backend + Auth)
4. **Frontend** (depends on BFF)
5. **Data Importer** (depends on Backend, runs on-demand)

***REMOVED******REMOVED*** 🏥 Health Checks

Each service includes health checks:

```bash
***REMOVED*** Check individual service health
curl http://localhost:8000/health  ***REMOVED*** Backend API
curl http://localhost:8003/health  ***REMOVED*** Auth API
curl http://localhost:8001/health  ***REMOVED*** BFF API
curl http://localhost:3000/api/health  ***REMOVED*** Frontend

***REMOVED*** Check all services
for port in 8000 8003 8001 3000; do
  echo "Checking port $port..."
  curl -f http://localhost:$port/health || echo "❌ Port $port unhealthy"
done
```

***REMOVED******REMOVED*** 📊 Monitoring

***REMOVED******REMOVED******REMOVED*** View Service Logs

```bash
***REMOVED*** All services
docker compose -f infra/compose/prod.yml logs -f

***REMOVED*** Specific service
docker compose -f infra/compose/prod.yml logs -f backend-api

***REMOVED*** Last 100 lines
docker compose -f infra/compose/prod.yml logs --tail=100 bff-api
```

***REMOVED******REMOVED******REMOVED*** Resource Usage

```bash
***REMOVED*** View resource usage
docker stats

***REMOVED*** View service resource limits
docker compose -f infra/compose/prod.yml config
```

***REMOVED******REMOVED******REMOVED*** Log Files

Persistent logs are stored in named volumes:

- `backend-logs:/app/logs`
- `auth-logs:/app/logs`
- `bff-logs:/app/logs`
- `importer-logs:/app/logs`

***REMOVED******REMOVED*** 🔒 Security Considerations

***REMOVED******REMOVED******REMOVED*** Production Security Checklist

- [ ] Strong JWT secret (32+ characters)
- [ ] Secure database password
- [ ] Internal API keys configured
- [ ] CORS origins properly configured
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules in place
- [ ] Regular security updates

***REMOVED******REMOVED******REMOVED*** Environment Variables

Never commit these to version control:

- `JWT_SECRET`
- `POSTGRES_PASSWORD`
- `INTERNAL_API_KEY`
- `TMDB_ACCESS_TOKEN`
- `OMDB_API_KEY`

***REMOVED******REMOVED*** 🚨 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Common Issues

**Service won't start:**

```bash
***REMOVED*** Check logs
docker compose -f infra/compose/prod.yml logs service-name

***REMOVED*** Check health
docker compose -f infra/compose/prod.yml ps
```

**Database connection issues:**

```bash
***REMOVED*** Verify PostgreSQL is running on host
sudo systemctl status postgresql

***REMOVED*** Check database connectivity
docker run --rm postgres:13 psql -h host.docker.internal -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;"
```

**Redis connection issues:**

```bash
***REMOVED*** Verify Redis is running on host
sudo systemctl status redis

***REMOVED*** Check Redis connectivity
docker run --rm redis:7 redis-cli -h host.docker.internal ping
```

***REMOVED******REMOVED******REMOVED*** Service Restart Order

If you need to restart services, follow this order:

1. Backend API
2. Auth API
3. BFF API
4. Frontend

```bash
***REMOVED*** Restart in correct order
docker compose -f infra/compose/prod.yml restart backend-api
docker compose -f infra/compose/prod.yml restart auth-api
docker compose -f infra/compose/prod.yml restart bff-api
docker compose -f infra/compose/prod.yml restart frontend
```

***REMOVED******REMOVED*** 📈 Performance Tuning

***REMOVED******REMOVED******REMOVED*** Resource Limits

Current resource limits per service:

- **Backend API**: 1 CPU, 1GB RAM
- **Auth API**: 0.5 CPU, 512MB RAM
- **BFF API**: 0.5 CPU, 512MB RAM
- **Frontend**: 0.5 CPU, 512MB RAM
- **Data Importer**: 0.5 CPU, 512MB RAM

***REMOVED******REMOVED******REMOVED*** Scaling

To scale services horizontally:

```bash
***REMOVED*** Scale BFF API to 2 instances
docker compose -f infra/compose/prod.yml up -d --scale bff-api=2

***REMOVED*** Scale with load balancer (requires additional configuration)
docker compose -f infra/compose/prod.yml up -d --scale backend-api=3
```

***REMOVED******REMOVED*** 🔄 Updates and Maintenance

***REMOVED******REMOVED******REMOVED*** Rolling Updates

```bash
***REMOVED*** Build new image
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:v2.0 .

***REMOVED*** Update environment file
sed -i 's/next-watch-backend:latest/next-watch-backend:v2.0/' .env.prod

***REMOVED*** Deploy update
docker compose -f infra/compose/prod.yml up -d --no-deps backend-api
```

***REMOVED******REMOVED******REMOVED*** Backup

```bash
***REMOVED*** Backup database
docker exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

***REMOVED*** Backup Redis
docker exec redis redis-cli BGSAVE
```

***REMOVED******REMOVED*** 📞 Support

For deployment issues:

1. Check service logs
2. Verify environment configuration
3. Ensure host services (PostgreSQL, Redis) are running
4. Check network connectivity between containers

***REMOVED******REMOVED*** 🎯 Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Database and Redis running on host
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy in place
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Rollback plan prepared
