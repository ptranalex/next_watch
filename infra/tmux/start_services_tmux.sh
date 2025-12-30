#!/usr/bin/env bash
# File: start_services_tmux.sh
# Start all Next Watch services locally within tmux

set -Eeuo pipefail

trap 'echo -e "${RED}❌ Error on line ${LINENO}: ${BASH_COMMAND}${NC}" >&2' ERR

SESSION="nextwatch"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Next Watch Services...${NC}"
echo -e "${CYAN}Project root: ${PROJECT_ROOT}${NC}"

# Cleanup function to stop any existing containers
cleanup_existing_containers() {
    echo -e "${YELLOW}🧹 Stopping any existing NextWatch containers...${NC}"
    # Only stop Qdrant container, keep Redis as Homebrew service
    docker stop nextwatch-qdrant 2>/dev/null || true
    docker rm nextwatch-qdrant 2>/dev/null || true
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Canonical list of expected tmux windows.
# Format: window_num|window_name|window_cmd
get_window_specs() {
    # NOTE: single-quoted heredoc to prevent the *launcher shell* from expanding
    # variables intended for the tmux window shells (set -u would crash).
    cat <<'EOF'
0|infra|echo '🔄 Checking Redis (Homebrew) service...' ; if ! redis-cli ping >/dev/null 2>&1; then echo '🚀 Starting Redis via Homebrew...' ; brew services start redis ; sleep 2 ; else echo '✅ Redis already running' ; fi ; echo '🔍 Infrastructure Status:' ; echo '🔴 Redis (Homebrew):' && redis-cli ping 2>/dev/null && echo '  ✅ Redis responding on localhost:6379' || echo '  ❌ Redis not responding' ; sleep 2
1|qdrant|echo '🔄 Starting Qdrant container with persistent storage...' && mkdir -p "$PROJECT_ROOT/data/qdrant_storage" && echo '📁 Storage directory ready' && docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v "$PROJECT_ROOT/data/qdrant_storage:/qdrant/storage" qdrant/qdrant
2|backend|cd "$PROJECT_ROOT/apps/backend-api" && echo '🔄 Starting Backend API on port 8000...' && hatch run install-libs && DB_URL='' ; for f in .env.local .env; do if [ -f "$f" ]; then DB_URL_LINE=$(grep -E '^[[:space:]]*DATABASE_URL=' "$f" | tail -n 1 || true) ; if [ -n "$DB_URL_LINE" ]; then DB_URL=${DB_URL_LINE#*=} ; fi ; fi ; done ; DB_URL=${DB_URL%\"} ; DB_URL=${DB_URL#\"} ; DB_URL=${DB_URL%$'\r'} ; if echo "$DB_URL" | grep -qE '^postgresql(\+|:)'; then echo '🗄️  Using PostgreSQL; running migrations...' && hatch run migrate ; else echo '🗄️  DATABASE_URL is not set to PostgreSQL; creating tables (SQLite-friendly) instead.' && echo '💡 To use Postgres migrations, set DATABASE_URL in apps/backend-api/.env(.local) and restart.' && hatch run db-init-tables ; fi && hatch run dev
3|bff|cd "$PROJECT_ROOT/apps/bff-api" && echo '🔄 Starting BFF API on port 8001...' && hatch run install-libs && hatch run dev
4|auth|cd "$PROJECT_ROOT/apps/auth-api" && echo '🔄 Starting Auth API on port 8003...' && hatch run install-libs && hatch run dev
5|reco|cd "$PROJECT_ROOT/apps/recommendation-api" && echo '🔄 Starting Recommendation API on port 8002...' && hatch run install-libs && hatch run dev
6|ml|cd "$PROJECT_ROOT/apps/ml-api" && echo '🔄 Starting ML API on port 8004...' && hatch run install-libs && hatch run dev
7|search|cd "$PROJECT_ROOT/apps/search-api" && echo '🔄 Starting Search API on port 8005...' && hatch run install-libs && hatch run dev
8|frontend|cd "$PROJECT_ROOT/apps/web-nextjs" && echo '🔄 Starting Next.js Frontend on port 3000...' && if [ ! -d node_modules ]; then pnpm install ; fi && pnpm dev
9|data|cd "$PROJECT_ROOT/apps/data-importer" && echo '📥 Data Importer ready. Use: hatch run cli sync movies --help'
10|monitoring|cd "$PROJECT_ROOT" && echo '🔍 Service status checker ready' && echo 'Use ./infra/scripts/check-services.sh to check all service status'
EOF
}

check_docker_daemon() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is installed but the Docker daemon is not running.${NC}"
        echo -e "${YELLOW}💡 Start Docker Desktop and retry.${NC}"
        exit 1
    fi
}

check_redis_ok_or_startable() {
    # Redis being already up is expected (Homebrew service). Treat that as OK.
    if redis-cli ping >/dev/null 2>&1; then
        return 0
    fi

    # If Redis is not responding but something else is listening on 6379, fail fast.
    if lsof -nP -iTCP:6379 -sTCP:LISTEN >/dev/null 2>&1; then
        echo -e "${RED}❌ Port 6379 is in use but Redis is not responding to redis-cli ping.${NC}"
        echo -e "${YELLOW}💡 Stop the process on 6379 or fix your Redis installation, then retry.${NC}"
        lsof -nP -iTCP:6379 -sTCP:LISTEN 2>/dev/null | sed 's/^/    /' || true
        exit 1
    fi
}

check_required_ports_available() {
    local ports=(6333 6334 8000 8001 8002 8003 8004 8005 3000)
    local conflicts=0

    for port in "${ports[@]}"; do
        if lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
            if [ $conflicts -eq 0 ]; then
                echo -e "${RED}❌ Port conflicts detected. Please stop the following listeners and retry:${NC}"
            fi
            echo -e "${RED}  - Port ${port} is already in use:${NC}"
            lsof -nP -iTCP:"${port}" -sTCP:LISTEN 2>/dev/null | sed 's/^/    /' || true
            conflicts=1
        fi
    done

    if [ $conflicts -ne 0 ]; then
        exit 1
    fi
}

# Check dependencies
echo -e "${YELLOW}⚙️  Checking dependencies...${NC}"
if ! command_exists tmux; then
    echo -e "${RED}❌ tmux is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command_exists hatch; then
    echo -e "${RED}❌ hatch is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command_exists pnpm; then
    echo -e "${RED}❌ pnpm is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${RED}❌ docker is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command_exists redis-cli; then
    echo -e "${RED}❌ redis-cli is not installed. Please install Redis via Homebrew first.${NC}"
    exit 1
fi

if ! command_exists brew; then
    echo -e "${RED}❌ brew is not installed. This script currently expects Homebrew-managed Redis on macOS.${NC}"
    exit 1
fi

# Function to check if a window exists
window_exists() {
    tmux list-windows -t "$SESSION" -F '#I' 2>/dev/null | grep -q "^$1$"
}

tmux_safe() {
    local desc="$1"
    shift

    if ! tmux "$@"; then
        echo -e "${RED}❌ tmux failed (${desc}).${NC}" >&2
        echo -e "${YELLOW}Command:${NC} tmux $*" >&2
        echo -e "${YELLOW}Current windows:${NC}" >&2
        tmux list-windows -t "$SESSION" -F '#I:#W' 2>/dev/null | sed 's/^/  /' >&2 || true
        exit 1
    fi
}

# Function to add a window if it doesn't exist
add_window_if_missing() {
    local window_num=$1
    local window_name=$2
    local window_cmd=$3

    if window_exists "$window_num"; then
        echo -e "${GREEN}✅ Window ${window_num} (${window_name}) exists${NC}"
        return 0
    else
        echo -e "${YELLOW}➕ Adding window ${window_num} (${window_name})${NC}"
        tmux new-window -t "$SESSION:$window_num" -n "$window_name"
        if [ -n "$window_cmd" ]; then
            tmux send-keys -t "$SESSION:$window_num" "PROJECT_ROOT=\"$PROJECT_ROOT\"; $window_cmd" C-m
        fi
        return 1
    fi
}

# Function to fix missing windows
fix_missing_windows() {
    echo -e "${BLUE}🔧 Checking and fixing missing windows...${NC}"
    local windows_added=0

    # If we need to add windows, Docker may be required (Qdrant). Validate daemon early.
    check_docker_daemon

    # Check all expected windows and add missing ones
    while IFS='|' read -r window_num window_name window_cmd; do
        add_window_if_missing "$window_num" "$window_name" "$window_cmd" || ((windows_added++))
    done < <(get_window_specs)

    if [ $windows_added -eq 0 ]; then
        echo -e "${GREEN}✅ All windows are present!${NC}"
    else
        echo -e "${GREEN}✅ Added $windows_added missing windows!${NC}"
    fi
}

# Handle existing session
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Session '$SESSION' already exists.${NC}"
    echo -e "${BLUE}Choose an option:${NC}"
    echo -e "  1. Attach to existing session"
    echo -e "  2. Kill and recreate session"
    echo -e "  3. Fix missing windows in existing session"
    if [ -t 0 ]; then
        read -p "Enter choice (1-3): " choice
    else
        choice=1
    fi

    case $choice in
        1)
            echo -e "${GREEN}Attaching to existing session...${NC}"
            tmux attach -t "$SESSION"
            exit 0
            ;;
        2)
            echo -e "${YELLOW}Killing existing session...${NC}"
            tmux kill-session -t "$SESSION"
            ;;
        3)
            fix_missing_windows
            echo -e "${GREEN}Attaching to updated session...${NC}"
            tmux attach -t "$SESSION"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Attaching to existing session...${NC}"
            tmux attach -t "$SESSION"
            exit 0
            ;;
    esac
fi

echo -e "${GREEN}✅ Creating new tmux session '$SESSION'${NC}"

echo -e "${YELLOW}🔎 Running preflight checks...${NC}"
check_docker_daemon
check_redis_ok_or_startable

# Clean up any existing containers first
cleanup_existing_containers

# After cleanup, ensure remaining required ports are free.
check_required_ports_available

# Create the session and first window for infrastructure
tmux new-session -d -s "$SESSION" -n infra

# Set the base index for windows to 0 (explicit) and ensure window 0 exists even if the
# user's tmux.conf defaults to base-index 1.
tmux_safe "set base-index" set-option -t "$SESSION" base-index 0
tmux_safe "enable renumber-windows" set-option -t "$SESSION" renumber-windows on

if ! window_exists 0; then
    first_window_num="$(tmux list-windows -t "$SESSION" -F '#I' | head -n 1)"
    tmux_safe "move first window to 0" move-window -s "$SESSION:$first_window_num" -t "$SESSION:0"
fi

echo -e "${BLUE}🏗️ Creating tmux windows (0-10) and starting services...${NC}"

while IFS='|' read -r window_num window_name window_cmd; do
    if [ "$window_num" = "0" ]; then
        tmux_safe "rename window 0" rename-window -t "$SESSION:0" "$window_name"
    else
        tmux_safe "create window $window_num ($window_name)" new-window -t "$SESSION:$window_num" -n "$window_name"
    fi

    if [ -n "$window_cmd" ]; then
        tmux_safe "send command to window $window_num ($window_name)" send-keys -t "$SESSION:$window_num" "PROJECT_ROOT=\"$PROJECT_ROOT\"; $window_cmd" C-m
    fi
done < <(get_window_specs)

# Verify all expected windows exist before continuing.
expected_missing=0
for expected in 0 1 2 3 4 5 6 7 8 9 10; do
    if ! window_exists "$expected"; then
        expected_missing=1
    fi
done
if [ "$expected_missing" -ne 0 ]; then
    echo -e "${RED}❌ Not all expected tmux windows (0-10) were created.${NC}" >&2
    tmux list-windows -t "$SESSION" -F '#I:#W' 2>/dev/null | sed 's/^/  /' >&2 || true
    exit 1
fi

# Go back to the infrastructure window (first window)
tmux select-window -t "$SESSION:0"

# Display helpful information
echo -e "${GREEN}🎉 Next Watch services are starting up!${NC}"
echo
echo -e "${CYAN}🏗️ Infrastructure Services:${NC}"
echo -e "  🔴 Redis (Homebrew):   http://localhost:6379"
echo -e "  🟠 Qdrant (Docker):    http://localhost:6333"
echo
echo -e "${CYAN}📋 Application Services:${NC}"
echo -e "  🔧 Backend API:        http://localhost:8000"
echo -e "  🌐 BFF API:            http://localhost:8001"
echo -e "  🤖 Recommendation API: http://localhost:8002"
echo -e "  🔐 Auth API:           http://localhost:8003"
echo -e "  🧠 ML API:             http://localhost:8004"
echo -e "  🔍 Search API:         http://localhost:8005"
echo -e "  🎨 Frontend:           http://localhost:3000"
echo
echo -e "${CYAN}📊 API Documentation:${NC}"
echo -e "  📖 Backend API docs:   http://localhost:8000/docs"
echo -e "  📖 BFF API docs:       http://localhost:8001/docs"
echo -e "  📖 Recommendation:     http://localhost:8002/docs"
echo -e "  📖 Auth API docs:      http://localhost:8003/docs"
echo -e "  📖 ML API docs:        http://localhost:8004/docs"
echo -e "  📖 Search API docs:    http://localhost:8005/docs"
echo
echo -e "${YELLOW}⏰ Services are starting up... This may take 1-2 minutes.${NC}"
echo -e "${YELLOW}💡 Use Ctrl+B then arrow keys to navigate between panes${NC}"
echo -e "${YELLOW}💡 Use Ctrl+B then number keys to switch between windows${NC}"
echo -e "${YELLOW}💡 Use Ctrl+B then 'd' to detach from session${NC}"
echo
echo -e "${PURPLE}🔧 Tmux Windows:${NC}"
echo -e "  0. infra      - Redis (Homebrew) infrastructure"
echo -e "  1. qdrant     - Qdrant vector database (Docker) with logs"
echo -e "  2. backend    - Backend API (port 8000)"
echo -e "  3. bff        - BFF API (port 8001)"
echo -e "  4. auth       - Auth API (port 8003)"
echo -e "  5. reco       - Recommendation API (port 8002)"
echo -e "  6. ml         - ML API (port 8004)"
echo -e "  7. search     - Search API (port 8005)"
echo -e "  8. frontend   - Next.js Frontend (port 3000)"
echo -e "  9. data       - Data Importer tools"
echo -e "  10. monitoring - Service status & health checks"
echo
echo -e "${GREEN}✅ Attaching to tmux session...${NC}"

# Attach to the session
tmux attach -t "$SESSION"
