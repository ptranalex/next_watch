# Environment Configuration (service routing)

This repo supports **direct service-to-service URLs** in development (recommended). If you run your own gateway/reverse-proxy, you can also route through it by changing URL env vars.

## Local development (recommended: direct URLs)

Put these variables in the relevant service env file (for example: `apps/bff-api/.env.local`).

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch
AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch_auth

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Service URLs (direct)
BACKEND_API_URL=http://localhost:8000
AUTH_API_URL=http://localhost:8003

# Environment Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## Production (behind a domain)

```bash
# Service URLs (via public domain / reverse proxy)
BACKEND_API_URL=https://your-domain.com/api
AUTH_API_URL=https://your-domain.com/auth

ENVIRONMENT=production
DEBUG=false
```

## Usage Instructions

1. Set the variables above in your service env file (recommended: `apps/bff-api/.env.local`).
2. Start the BFF:

```bash
cd apps/bff-api
hatch env create
cp env.example .env
./setup-local-deps.sh
hatch run dev
```
