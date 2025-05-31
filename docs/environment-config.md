***REMOVED*** Environment Configuration for API Gateway Routing

***REMOVED******REMOVED*** BFF Traffic Through Gateway

To ensure BFF routes traffic through the API gateway, configure these environment variables:

***REMOVED******REMOVED******REMOVED*** Local Development (.env.local)

```bash
***REMOVED*** Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch
AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/next_watch_auth

***REMOVED*** Redis Configuration
REDIS_URL=redis://localhost:6379/0

***REMOVED*** JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

***REMOVED*** Service URLs - Route through Gateway (Recommended)
BACKEND_API_URL=http://localhost:8080/api
AUTH_SERVICE_URL=http://localhost:8080/auth

***REMOVED*** Alternative - Direct Service Access (For debugging)
***REMOVED*** BACKEND_API_URL=http://localhost:8000
***REMOVED*** AUTH_SERVICE_URL=http://localhost:8003

***REMOVED*** Environment Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

***REMOVED******REMOVED******REMOVED*** Production Configuration

```bash
***REMOVED*** Service URLs - Production Gateway
BACKEND_API_URL=https://your-domain.com/api
AUTH_SERVICE_URL=https://your-domain.com/auth

ENVIRONMENT=production
DEBUG=false
```

***REMOVED******REMOVED*** Usage Instructions

1. Copy the configuration above to `.env.local`
2. Start your services locally:

   ```bash
   ***REMOVED*** Terminal 1: Start gateway
   ./scripts/gateway.sh local-dev

   ***REMOVED*** Terminal 2: Start BFF with gateway routing
   cd apps/bff-api
   poetry run bff-api serve
   ```

3. BFF will now route through the gateway!
