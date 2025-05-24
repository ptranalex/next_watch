***REMOVED*** Next Watch Authentication API

Dedicated microservice for authentication and token management in the Next Watch movie platform.

***REMOVED******REMOVED*** 🎯 Purpose

This service handles all authentication concerns in the new microservices architecture:

- User registration and login
- JWT token generation and validation
- Token verification for BFF service
- Centralized authentication logic

***REMOVED******REMOVED*** 🏗️ Architecture Role

```
Frontend → BFF → Auth-API (verify token) → Backend-API (X-User-ID header)
```

- **Frontend** sends tokens to BFF
- **BFF** validates tokens via Auth-API `/auth/verify-token`
- **Auth-API** returns user info if token is valid
- **BFF** injects `X-User-ID` header for Backend-API calls

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.9+
- Poetry
- PostgreSQL database (shared with other services)

***REMOVED******REMOVED******REMOVED*** Setup

1. **Install dependencies:**

   ```bash
   cd apps/auth-api
   poetry install
   ```

2. **Set environment variables:**

   ```bash
   ***REMOVED*** Copy example env (if available)
   cp .env.example .env.local

   ***REMOVED*** Or set manually:
   export DATABASE_URL="postgresql://user:pass@localhost:5432/next_watch"
   export JWT_SECRET="your-secret-key"
   export AUTH_API_PORT=8003
   ```

3. **Run the service:**

   ```bash
   ***REMOVED*** Development with auto-reload
   poetry run auth-api serve --reload

   ***REMOVED*** Or directly with uvicorn
   poetry run uvicorn src.auth_api.main:app --reload --port 8003
   ```

4. **Verify it's running:**
   ```bash
   curl http://localhost:8003/health
   ```

***REMOVED******REMOVED*** 📡 API Endpoints

***REMOVED******REMOVED******REMOVED*** Health & Info

- `GET /` - Service information
- `GET /health` - Health check
- `GET /health/db` - Database health check

***REMOVED******REMOVED******REMOVED*** Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with form data
- `POST /auth/login/json` - Login with JSON
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

***REMOVED******REMOVED******REMOVED*** Token Verification (for BFF)

- `POST /auth/verify-token` - Verify JWT token and return user info

***REMOVED******REMOVED*** 🔧 Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

| Variable                      | Default          | Description                |
| ----------------------------- | ---------------- | -------------------------- |
| `DATABASE_URL`                | postgresql://... | Database connection URL    |
| `AUTH_API_PORT`               | 8003             | Port for the auth service  |
| `JWT_SECRET`                  | (required)       | Secret key for JWT signing |
| `JWT_ALGORITHM`               | HS256            | JWT signing algorithm      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30               | Access token expiration    |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | 7                | Refresh token expiration   |
| `DEBUG`                       | false            | Enable debug mode          |
| `LOG_LEVEL`                   | INFO             | Logging level              |

***REMOVED******REMOVED*** 🔐 Security

- **JWT Tokens**: Uses industry-standard JWT for authentication
- **Password Hashing**: Bcrypt with salting
- **Token Expiration**: Configurable access and refresh token lifetimes
- **Environment Isolation**: Separate configuration for dev/prod

***REMOVED******REMOVED*** 🧪 Usage Examples

***REMOVED******REMOVED******REMOVED*** Register a User

```bash
curl -X POST http://localhost:8003/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

***REMOVED******REMOVED******REMOVED*** Login

```bash
curl -X POST http://localhost:8003/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

***REMOVED******REMOVED******REMOVED*** Verify Token (BFF Usage)

```bash
curl -X POST http://localhost:8003/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

***REMOVED******REMOVED*** 🐳 Docker

***REMOVED******REMOVED******REMOVED*** Build Image

```bash
docker build -t next-watch-auth-api .
```

***REMOVED******REMOVED******REMOVED*** Run Container

```bash
docker run -p 8003:8003 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/next_watch" \
  -e JWT_SECRET="your-secret-key" \
  next-watch-auth-api
```

***REMOVED******REMOVED*** 🔨 Development

***REMOVED******REMOVED******REMOVED*** Run Tests

```bash
poetry run pytest
```

***REMOVED******REMOVED******REMOVED*** Code Quality

```bash
***REMOVED*** Format code
poetry run black src/

***REMOVED*** Check types
poetry run mypy src/

***REMOVED*** Lint
poetry run flake8 src/
```

***REMOVED******REMOVED******REMOVED*** CLI Commands

```bash
***REMOVED*** Start server
poetry run auth-api serve --host 0.0.0.0 --port 8003 --reload

***REMOVED*** Health check
poetry run auth-api health
```

***REMOVED******REMOVED*** 🌐 Integration

***REMOVED******REMOVED******REMOVED*** With BFF Service

The BFF service should call the auth verification endpoint:

```python
***REMOVED*** In BFF
async def verify_user_token(token: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-api:8003/auth/verify-token",
            json={"token": token}
        )

        if response.status_code == 200:
            data = response.json()
            if data["valid"]:
                return {
                    "user_id": data["user_id"],
                    "email": data["email"],
                    "username": data["username"]
                }
    return None
```

***REMOVED******REMOVED*** 📝 Notes

- This service replaces the auth functionality previously in `backend-api`
- Database tables are shared with other services (managed centrally)
- JWT secret must be the same across all services that generate/validate tokens
- Service runs on port 8003 by default to avoid conflicts

***REMOVED******REMOVED*** 🔄 Migration from backend-api

If migrating from embedded auth in backend-api:

1. Update BFF to call this service for token verification
2. Remove auth routes from backend-api
3. Update frontend to use new auth endpoints (if needed)
4. Ensure JWT_SECRET is consistent across services
