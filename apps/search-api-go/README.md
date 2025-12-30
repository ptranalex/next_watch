# Search API (Go)

Minimal Go scaffold for the Search API runtime service.

## Run locally

```bash
cd apps/search-api-go
go run ./cmd/search-api
```

Then:

- `GET http://localhost:8080/health`

## Configuration (env)

- `PORT` (default: `8080`)
- `ENV` (default: `dev`)
- `LOG_LEVEL` (default: `info`) one of: `trace|debug|info|warn|error|fatal|panic`
- `REDIS_URL` (optional) e.g. `redis://localhost:6379/0`
