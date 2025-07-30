***REMOVED*** Next Watch Tmux Development Environment

This directory contains scripts to start all Next Watch services in a convenient tmux session for local development.

***REMOVED******REMOVED*** Quick Start

```bash
***REMOVED*** From project root
./infra/tmux/start_services_tmux.sh
```

***REMOVED******REMOVED*** What It Does

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

***REMOVED******REMOVED*** Smart Session Management

When running the script, if a session already exists, you'll get options:

1. **Attach to existing session** - Connect to what's already running
2. **Kill and recreate session** - Fresh start with all services
3. **Fix missing windows** - Automatically detect and add any missing windows

This means you can safely run the script multiple times without losing your work!

***REMOVED******REMOVED*** Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000 (docs: http://localhost:8000/docs)
- **BFF API**: http://localhost:8001 (docs: http://localhost:8001/docs)
- **Recommendation API**: http://localhost:8002 (docs: http://localhost:8002/docs)
- **Auth API**: http://localhost:8003 (docs: http://localhost:8003/docs)
- **ML API**: http://localhost:8004 (docs: http://localhost:8004/docs)
- **Search API**: http://localhost:8005 (docs: http://localhost:8005/docs)
- **Redis (Homebrew)**: localhost:6379
- **Qdrant (Docker)**: http://localhost:6333

***REMOVED******REMOVED*** Prerequisites

***REMOVED******REMOVED******REMOVED*** Required Tools

```bash
***REMOVED*** macOS
brew install tmux hatch pnpm redis docker

***REMOVED*** Ubuntu/Debian
sudo apt update
sudo apt install tmux docker.io
***REMOVED*** Install Node.js 18+ and pnpm
***REMOVED*** Install hatch: pip install hatch
***REMOVED*** Install Redis via package manager or build from source
```

***REMOVED******REMOVED******REMOVED*** Database Dependencies

**Redis**: Managed automatically via Homebrew. The script will start the Redis service if it's not already running.

**Qdrant**: Started automatically as a Docker container.

**PostgreSQL**: You need to set this up separately for the backend API.

```bash
***REMOVED*** Install and start PostgreSQL
brew install postgresql@14
brew services start postgresql@14

***REMOVED*** Create database
createdb nextwatch_dev
```

***REMOVED******REMOVED*** Navigation

***REMOVED******REMOVED******REMOVED*** Tmux Basics

- `Ctrl+B` then `0-9` - Switch to window 0-9
- `Ctrl+B` then `:select-window -t 10` - Switch to window 10 (monitoring)
- `Ctrl+B` then `w` - Show window list (easier navigation)
- `Ctrl+B` then `arrow keys` - Switch between panes
- `Ctrl+B` then `d` - Detach from session
- `Ctrl+B` then `?` - Show help

***REMOVED******REMOVED******REMOVED*** Quick Window Access

- `Ctrl+B` then `0` - infra (Redis)
- `Ctrl+B` then `1` - qdrant (Vector DB logs)
- `Ctrl+B` then `2` - backend API
- `Ctrl+B` then `8` - frontend
- `Ctrl+B` then `w` then arrow keys - Browse all windows

***REMOVED******REMOVED******REMOVED*** Reconnect to Session

```bash
tmux attach -t nextwatch
```

***REMOVED******REMOVED******REMOVED*** Kill Session

```bash
tmux kill-session -t nextwatch
```

***REMOVED******REMOVED*** Health Monitoring

In the monitoring window (window 10), run:

```bash
./infra/scripts/check-services.sh
```

This shows the status of all services including:

- Redis (Homebrew service)
- Qdrant (Docker container) with persistent storage
- All API services
- Frontend application

***REMOVED******REMOVED******REMOVED*** Viewing Live Logs

- **Qdrant logs**: Switch to window 1 (`Ctrl+B` then `1`) to see real-time Qdrant vector database logs
- **API logs**: Each service runs in its own window with live output
- **All services**: Use `Ctrl+B` then `w` to navigate between windows

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Redis Issues

```bash
***REMOVED*** Check Redis status
redis-cli ping

***REMOVED*** Start Redis manually
brew services start redis

***REMOVED*** Check Redis logs
brew services list | grep redis
```

***REMOVED******REMOVED******REMOVED*** Qdrant Issues

```bash
***REMOVED*** Check if Qdrant container is running
docker ps | grep qdrant

***REMOVED*** View Qdrant logs in real-time
***REMOVED*** Switch to window 1 in tmux session: Ctrl+B then 1

***REMOVED*** Restart Qdrant container (with persistent storage)
docker stop nextwatch-qdrant
tmux new-window -t nextwatch:1 -n qdrant
tmux send-keys -t nextwatch:qdrant "cd /path/to/project && docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/data/qdrant_storage:/qdrant/storage qdrant/qdrant" C-m

***REMOVED*** Check Qdrant API
curl http://localhost:6333/collections
```

***REMOVED******REMOVED******REMOVED*** Service Won't Start

- Check logs in the respective tmux window
- Ensure all dependencies are installed
- Check if ports are already in use: `lsof -i :8000`

***REMOVED******REMOVED******REMOVED*** Clean Restart

```bash
***REMOVED*** Option 1: Use the built-in session management
./infra/tmux/start_services_tmux.sh
***REMOVED*** Choose option 2 to kill and recreate

***REMOVED*** Option 2: Manual cleanup
tmux kill-session -t nextwatch
docker stop nextwatch-qdrant 2>/dev/null || true
docker rm nextwatch-qdrant 2>/dev/null || true

***REMOVED*** Start fresh
./infra/tmux/start_services_tmux.sh
```

***REMOVED******REMOVED******REMOVED*** Missing Windows

If you notice missing windows (common issue):

```bash
***REMOVED*** Use built-in repair
./infra/tmux/start_services_tmux.sh
***REMOVED*** Choose option 3 to fix missing windows

***REMOVED*** This will automatically:
***REMOVED*** - Detect which windows should exist (0-10)
***REMOVED*** - Add any missing windows
***REMOVED*** - Start the appropriate services
***REMOVED*** - Preserve existing working windows
```

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** Data Persistence

- **Redis**: Data persists between restarts (Homebrew manages persistence)
- **Qdrant**: Data persists in `./qdrant_storage/` directory (vector embeddings saved!)
- **PostgreSQL**: Separate setup required, data persists independently

***REMOVED******REMOVED******REMOVED*** Smart Window Management

- **Missing window detection**: Script automatically detects and fixes missing windows
- **Flexible session handling**: Attach, recreate, or repair existing sessions
- **Proper window numbering**: Windows 0-10 for consistent navigation

***REMOVED******REMOVED******REMOVED*** Live Monitoring

- **Real-time logs**: Each service has its own window with live output
- **Dedicated Qdrant logs**: Window 1 shows vector database activity
- **Health monitoring**: Window 10 provides service status checking

***REMOVED******REMOVED*** Notes

- Services take 1-2 minutes to fully start up
- Frontend hot-reload works automatically
- API services restart automatically on code changes (via hatch)
- Qdrant embeddings and collections persist between sessions
- Use `Ctrl+B` then `w` for easy window navigation
- The script is safe to run multiple times
