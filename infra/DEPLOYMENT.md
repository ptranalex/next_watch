# Next Watch Production Deployment Guide

This guide covers deploying the complete Next Watch application stack using Docker Compose.

## 🏗️ Architecture Overview

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

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have the following installed:

- Docker (20.10+)
- Docker Compose (2.0+)
- PostgreSQL (running on host)
- Redis (running on host)

### 2. Environment Setup

```bash
# Copy the environment template
cp infra/env/prod.example .env.prod

# Edit the environment file with your values
nano .env.prod
```

### 3. Build and Deploy

```bash
# Make the deployment script executable
chmod +x scripts/deploy-prod.sh

# Run the complete deployment
./scripts/deploy-prod.sh

# Or build and deploy with data import
./scripts/deploy-prod.sh --import
```

## 📋 Individual Docker Build Commands

### Build All Services

```bash
# Backend API
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest .

# Auth API
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest .

# BFF API
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest .

# Frontend
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest .

# Data Importer
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest .
```

### Build All in Parallel

```bash
# Build all services simultaneously for faster builds
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:latest . &
docker build -f apps/auth-api/Dockerfile -t next-watch-auth:latest . &
docker build -f apps/bff-api/Dockerfile -t next-watch-bff:latest . &
docker build -f apps/web-nextjs/Dockerfile -t next-watch-frontend:latest . &
docker build -f apps/data-importer/Dockerfile -t next-watch-importer:latest . &
wait
echo "✅ All builds completed"
```

## 🐳 Docker Compose Commands

### Basic Operations

```bash
# Start all services
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d

# Stop all services
docker compose -f infra/compose/prod.yml --env-file .env.prod down

# View service status
docker compose -f infra/compose/prod.yml --env-file .env.prod ps

# View logs for all services
docker compose -f infra/compose/prod.yml --env-file .env.prod logs -f

# View logs for specific service
docker compose -f infra/compose/prod.yml --env-file .env.prod logs -f backend-api
```

### Service Management

```bash
# Restart a specific service
docker compose -f infra/compose/prod.yml --env-file .env.prod restart backend-api

# Scale a service (if needed)
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d --scale bff-api=2

# Update a single service
docker compose -f infra/compose/prod.yml --env-file .env.prod up -d --no-deps backend-api
```

### Data Import

```bash
# Run data import (one-time)
docker compose -f infra/compose/prod.yml --env-file .env.prod --profile import up data-importer

# Run data sync (scheduled)
docker compose -f infra/compose/prod.yml --env-file .env.prod --profile sync up data-importer
```

## 🔧 Configuration

### Required Environment Variables

Create `.env.prod` with these essential variables:

```bash
# Docker Images
DOCKER_BACKEND_IMAGE=next-watch-backend:latest
DOCKER_AUTH_IMAGE=next-watch-auth:latest
DOCKER_BFF_IMAGE=next-watch-bff:latest
DOCKER_FRONTEND_IMAGE=next-watch-frontend:latest
DOCKER_IMPORTER_IMAGE=next-watch-importer:latest

# Database
POSTGRES_USER=next_watch_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=next_watch

# Security
JWT_SECRET=your-super-secure-jwt-secret-key
INTERNAL_API_KEY=your-internal-api-key

# External APIs
TMDB_ACCESS_TOKEN=your-tmdb-token
OMDB_API_KEY=your-omdb-key
```

### Service Dependencies

The services start in this order due to health check dependencies:

1. **Backend API** (core service)
2. **Auth API** (authentication)
3. **BFF API** (depends on Backend + Auth)
4. **Frontend** (depends on BFF)
5. **Data Importer** (depends on Backend, runs on-demand)

## 🏥 Health Checks

Each service includes health checks:

```bash
# Check individual service health
curl http://localhost:8000/health  # Backend API
curl http://localhost:8003/health  # Auth API
curl http://localhost:8001/health  # BFF API
curl http://localhost:3000/api/health  # Frontend

# Check all services
for port in 8000 8003 8001 3000; do
  echo "Checking port $port..."
  curl -f http://localhost:$port/health || echo "❌ Port $port unhealthy"
done
```

## 📊 Monitoring

### View Service Logs

```bash
# All services
docker compose -f infra/compose/prod.yml logs -f

# Specific service
docker compose -f infra/compose/prod.yml logs -f backend-api

# Last 100 lines
docker compose -f infra/compose/prod.yml logs --tail=100 bff-api
```

### Resource Usage

```bash
# View resource usage
docker stats

# View service resource limits
docker compose -f infra/compose/prod.yml config
```

### Log Files

Persistent logs are stored in named volumes:

- `backend-logs:/app/logs`
- `auth-logs:/app/logs`
- `bff-logs:/app/logs`
- `importer-logs:/app/logs`

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Strong JWT secret (32+ characters)
- [ ] Secure database password
- [ ] Internal API keys configured
- [ ] CORS origins properly configured
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules in place
- [ ] Regular security updates

### Environment Variables

Never commit these to version control:

- `JWT_SECRET`
- `POSTGRES_PASSWORD`
- `INTERNAL_API_KEY`
- `TMDB_ACCESS_TOKEN`
- `OMDB_API_KEY`

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**

```bash
# Check logs
docker compose -f infra/compose/prod.yml logs service-name

# Check health
docker compose -f infra/compose/prod.yml ps
```

**Database connection issues:**

```bash
# Verify PostgreSQL is running on host
sudo systemctl status postgresql

# Check database connectivity
docker run --rm postgres:13 psql -h host.docker.internal -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;"
```

**Redis connection issues:**

```bash
# Verify Redis is running on host
sudo systemctl status redis

# Check Redis connectivity
docker run --rm redis:7 redis-cli -h host.docker.internal ping
```

### Service Restart Order

If you need to restart services, follow this order:

1. Backend API
2. Auth API
3. BFF API
4. Frontend

```bash
# Restart in correct order
docker compose -f infra/compose/prod.yml restart backend-api
docker compose -f infra/compose/prod.yml restart auth-api
docker compose -f infra/compose/prod.yml restart bff-api
docker compose -f infra/compose/prod.yml restart frontend
```

## 📈 Performance Tuning

### Resource Limits

Current resource limits per service:

- **Backend API**: 1 CPU, 1GB RAM
- **Auth API**: 0.5 CPU, 512MB RAM
- **BFF API**: 0.5 CPU, 512MB RAM
- **Frontend**: 0.5 CPU, 512MB RAM
- **Data Importer**: 0.5 CPU, 512MB RAM

### Scaling

To scale services horizontally:

```bash
# Scale BFF API to 2 instances
docker compose -f infra/compose/prod.yml up -d --scale bff-api=2

# Scale with load balancer (requires additional configuration)
docker compose -f infra/compose/prod.yml up -d --scale backend-api=3
```

## 🔄 Updates and Maintenance

### Rolling Updates

```bash
# Build new image
docker build -f apps/backend-api/Dockerfile -t next-watch-backend:v2.0 .

# Update environment file
sed -i 's/next-watch-backend:latest/next-watch-backend:v2.0/' .env.prod

# Deploy update
docker compose -f infra/compose/prod.yml up -d --no-deps backend-api
```

### Backup

```bash
# Backup database
docker exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Backup Redis
docker exec redis redis-cli BGSAVE
```

## 📞 Support

For deployment issues:

1. Check service logs
2. Verify environment configuration
3. Ensure host services (PostgreSQL, Redis) are running
4. Check network connectivity between containers

## 🎯 Production Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Database and Redis running on host
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy in place
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Rollback plan prepared
