# Next Watch Tmux Development Environment

This directory contains scripts to start all Next Watch services in a convenient tmux session for local development.

## Quick Start

```bash
# From project root
./infra/tmux/start_services_tmux.sh
```

## What It Does

The script creates an 11-window tmux session called "nextwatch" with:

0. **infra** - Redis (Homebrew service) on port 6379
1. **qdrant** - Qdrant vector database (Docker) on port 6333 with live logs
2. **backend** - Backend API on port 8000
3. **bff** - BFF API on port 8001
4. **auth** - Auth API on port 8003
5. **reco** - Recommendation API on port 8002
6. **ml** - ML API on port 8004
7. **search** - Search API on port 8005
8. **frontend** - Next.js frontend on port 3000
9. **data** - Data importer utilities
10. **monitoring** - Service health checks and monitoring

## Smart Session Management

When running the script, if a session already exists, you'll get options:

1. **Attach to existing session** - Connect to what's already running
2. **Kill and recreate session** - Fresh start with all services
3. **Fix missing windows** - Automatically detect and add any missing windows

This means you can safely run the script multiple times without losing your work!

## Optional: Disable Specific Windows (Env Toggles)

By default, the script starts all windows `0-10`. You can disable individual services by setting `NEXTWATCH_ENABLE_*` environment variables to `0`.

- Disabled windows are still created at their normal indices (to preserve navigation), but they will print a “disabled” message instead of starting the service.

Examples:

```bash
# Skip frontend
NEXTWATCH_ENABLE_FRONTEND=0 ./infra/tmux/start_services_tmux.sh

# Skip Qdrant (no Docker needed)
NEXTWATCH_ENABLE_QDRANT=0 ./infra/tmux/start_services_tmux.sh
```

## Service URLs

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000` (docs: `http://localhost:8000/docs`)
- **BFF API**: `http://localhost:8001` (docs: `http://localhost:8001/docs`)
- **Recommendation API**: `http://localhost:8002` (docs: `http://localhost:8002/docs`)
- **Auth API**: `http://localhost:8003` (docs: `http://localhost:8003/docs`)
- **ML API**: `http://localhost:8004` (docs: `http://localhost:8004/docs`)
- **Search API**: `http://localhost:8005` (docs: `http://localhost:8005/docs`)
- **Redis (Homebrew)**: `localhost:6379`
- **Qdrant (Docker)**: `http://localhost:6333`

## Prerequisites

### Required Tools

```bash
# macOS
brew install tmux hatch pnpm redis docker

# Ubuntu/Debian
sudo apt update
sudo apt install tmux docker.io
# Install Node.js 18+ and pnpm
# Install hatch: pip install hatch
# Install Redis via package manager or build from source
```

### Database Dependencies

**Redis**: Managed automatically via Homebrew. The script will start the Redis service if it's not already running.

**Qdrant**: Started automatically as a Docker container.

**PostgreSQL**: You need to set this up separately for the backend API.

```bash
# Install and start PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb nextwatch_dev
```

## Navigation

### Tmux Basics

- `Ctrl+B` then `0-9` - Switch to window 0-9
- `Ctrl+B` then `:select-window -t 10` - Switch to window 10 (monitoring)
- `Ctrl+B` then `w` - Show window list (easier navigation)
- `Ctrl+B` then `arrow keys` - Switch between panes
- `Ctrl+B` then `d` - Detach from session
- `Ctrl+B` then `?` - Show help

### Quick Window Access

- `Ctrl+B` then `0` - infra (Redis)
- `Ctrl+B` then `1` - qdrant (Vector DB logs)
- `Ctrl+B` then `2` - backend API
- `Ctrl+B` then `8` - frontend
- `Ctrl+B` then `w` then arrow keys - Browse all windows

### Reconnect to Session

```bash
tmux attach -t nextwatch
```

### Kill Session

```bash
tmux kill-session -t nextwatch
```

## Health Monitoring

In the monitoring window (window 10), run:

```bash
./infra/scripts/check-services.sh
```

This shows the status of all services including:

- Redis (Homebrew service)
- Qdrant (Docker container) with persistent storage
- All API services
- Frontend application

### Viewing Live Logs

- **Qdrant logs**: Switch to window 1 (`Ctrl+B` then `1`) to see real-time Qdrant vector database logs
- **API logs**: Each service runs in its own window with live output
- **All services**: Use `Ctrl+B` then `w` to navigate between windows

## Troubleshooting

### Redis Issues

```bash
# Check Redis status
redis-cli ping

# Start Redis manually
brew services start redis

# Check Redis logs
brew services list | grep redis
```

### Qdrant Issues

```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# View Qdrant logs in real-time
# Switch to window 1 in tmux session: Ctrl+B then 1

# Restart Qdrant container (with persistent storage)
docker stop nextwatch-qdrant
tmux new-window -t nextwatch:1 -n qdrant
tmux send-keys -t nextwatch:qdrant "cd /path/to/project && docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/data/qdrant_storage:/qdrant/storage qdrant/qdrant" C-m

# Check Qdrant API
curl http://localhost:6333/collections
```

### Service Won't Start

- Check logs in the respective tmux window
- Ensure all dependencies are installed
- Check if ports are already in use: `lsof -i :8000`
- The tmux starter script now aborts early if app/Qdrant ports are already in use (3000, 6333/6334, 8000–8005). If you already have a `nextwatch` tmux session running, just attach to it instead: `tmux attach -t nextwatch`.

### Clean Restart

```bash
# Option 1: Use the built-in session management
./infra/tmux/start_services_tmux.sh
# Choose option 2 to kill and recreate

# Option 2: Manual cleanup
tmux kill-session -t nextwatch
docker stop nextwatch-qdrant 2>/dev/null || true
docker rm nextwatch-qdrant 2>/dev/null || true

# Start fresh
./infra/tmux/start_services_tmux.sh
```

### Missing Windows

If you notice missing windows (common issue):

```bash
# Use built-in repair
./infra/tmux/start_services_tmux.sh
# Choose option 3 to fix missing windows

# This will automatically:
# - Detect which windows should exist (0-10)
# - Add any missing windows
# - Start the appropriate services
# - Preserve existing working windows
```

## Features

### Data Persistence

- **Redis**: Data persists between restarts (Homebrew manages persistence)
- **Qdrant**: Data persists in `./data/qdrant_storage/` directory (vector embeddings saved!)
- **PostgreSQL**: Separate setup required, data persists independently

### Smart Window Management

- **Missing window detection**: Script automatically detects and fixes missing windows
- **Flexible session handling**: Attach, recreate, or repair existing sessions
- **Proper window numbering**: Windows 0-10 for consistent navigation

### Live Monitoring

- **Real-time logs**: Each service has its own window with live output
- **Dedicated Qdrant logs**: Window 1 shows vector database activity
- **Health monitoring**: Window 10 provides service status checking

## Notes

- Services take 1-2 minutes to fully start up
- Frontend hot-reload works automatically
- API services restart automatically on code changes (via hatch)
- On startup, the backend window initializes schema automatically:
  - If `DATABASE_URL` is PostgreSQL (configured in `apps/backend-api/.env` or `.env.local`), it runs `hatch run migrate`
  - Otherwise it falls back to `hatch run db-init-tables` (SQLite-friendly)
- Qdrant embeddings and collections persist between sessions
- Use `Ctrl+B` then `w` for easy window navigation
- The script is safe to run multiple times
