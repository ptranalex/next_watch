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

#
# -----------------------------------------------------------------------------
# Spec / config (single-file refactor)
# -----------------------------------------------------------------------------
#
# Minor UX improvement: allow disabling specific windows without changing the
# default behavior. Windows still exist at indices 0-10 (to preserve navigation),
# but a disabled window will just print a message instead of starting the service.
#
# Examples:
#   NEXTWATCH_ENABLE_FRONTEND=0 ./infra/tmux/start_services_tmux.sh
#   NEXTWATCH_ENABLE_QDRANT=0   ./infra/tmux/start_services_tmux.sh
#

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

require_cmd() {
    local cmd="$1"
    local hint="${2:-}"

    if ! command_exists "$cmd"; then
        echo -e "${RED}❌ Missing dependency: ${cmd}${NC}"
        if [ -n "$hint" ]; then
            echo -e "${YELLOW}💡 ${hint}${NC}"
        fi
        exit 1
    fi
}

_to_upper() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

is_enabled() {
    local key
    key="$(_to_upper "$1")"
    local env_key="NEXTWATCH_ENABLE_${key}"
    local raw="${!env_key:-1}"

    case "$raw" in
        0 | "false" | "FALSE" | "no" | "NO" | "off" | "OFF")
            return 1
            ;;
        *)
            return 0
            ;;
    esac
}

_disabled_cmd() {
    local key="$1"
    local name="$2"
    local env_key="NEXTWATCH_ENABLE_$(_to_upper "$key")"
    printf "%s" "echo '⏸️  ${name} is disabled (${env_key}=0).'; echo 'Set ${env_key}=1 to enable and restart this window.'"
}

_cmd_infra() {
    printf "%s" "echo '🔄 Checking Redis (Homebrew) service...' ; if ! redis-cli ping >/dev/null 2>&1; then echo '🚀 Starting Redis via Homebrew...' ; brew services start redis ; sleep 2 ; else echo '✅ Redis already running' ; fi ; echo '🔍 Infrastructure Status:' ; echo '🔴 Redis (Homebrew):' && redis-cli ping 2>/dev/null && echo '  ✅ Redis responding on localhost:6379' || echo '  ❌ Redis not responding' ; sleep 2"
}

_cmd_qdrant() {
    printf "%s" "echo '🔄 Starting Qdrant container with persistent storage...' && mkdir -p \"$PROJECT_ROOT/data/qdrant_storage\" && echo '📁 Storage directory ready' && docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v \"$PROJECT_ROOT/data/qdrant_storage:/qdrant/storage\" qdrant/qdrant"
}

_cmd_backend() {
    # NOTE: We keep this SQLite/Postgres detection local to the backend window.
    # SQLite can't run the full migration set; Postgres can.
    printf "%s" "cd \"$PROJECT_ROOT/apps/backend-api\" && echo '🔄 Starting Backend API on port 8000...' && hatch run install-libs && DB_URL='' ; for f in .env.local .env; do if [ -f \"$f\" ]; then DB_URL_LINE=$(grep -E '^[[:space:]]*DATABASE_URL=' \"$f\" | tail -n 1 || true) ; if [ -n \"$DB_URL_LINE\" ]; then DB_URL=\${DB_URL_LINE#*=} ; fi ; fi ; done ; DB_URL=\${DB_URL%\\\"} ; DB_URL=\${DB_URL#\\\"} ; DB_URL=\${DB_URL%$'\\r'} ; if echo \"\$DB_URL\" | grep -qE '^postgresql(\\+|:)'; then echo '🗄️  Using PostgreSQL; running migrations...' && hatch run migrate ; else echo '🗄️  DATABASE_URL is not set to PostgreSQL; creating tables (SQLite-friendly) instead.' && echo '💡 To use Postgres migrations, set DATABASE_URL in apps/backend-api/.env(.local) and restart.' && hatch run db-init-tables ; fi && hatch run dev"
}

_cmd_bff() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/bff-api\" && echo '🔄 Starting BFF API on port 8001...' && hatch run install-libs && hatch run dev"
}

_cmd_auth() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/auth-api\" && echo '🔄 Starting Auth API on port 8003...' && hatch run install-libs && hatch run dev"
}

_cmd_reco() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/recommendation-api\" && echo '🔄 Starting Recommendation API on port 8002...' && hatch run install-libs && hatch run dev"
}

_cmd_ml() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/ml-api\" && echo '🔄 Starting ML API on port 8004...' && hatch run install-libs && hatch run dev"
}

_cmd_search() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/search-api\" && echo '🔄 Starting Search API on port 8005...' && hatch run install-libs && hatch run dev"
}

_cmd_frontend() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/web-nextjs\" && echo '🔄 Starting Next.js Frontend on port 3000...' && if [ ! -d node_modules ]; then pnpm install ; fi && pnpm dev"
}

_cmd_data() {
    printf "%s" "cd \"$PROJECT_ROOT/apps/data-importer\" && echo '📥 Data Importer ready. Use: hatch run cli sync movies --help'"
}

_cmd_monitoring() {
    printf "%s" "cd \"$PROJECT_ROOT\" && echo '🔍 Service status checker ready' && echo 'Use ./infra/scripts/check-services.sh to check all service status'"
}

_window_cmd() {
    local key="$1"
    local name="$2"
    local cmd="$3"

    if is_enabled "$key"; then
        printf "%s" "$cmd"
    else
        _disabled_cmd "$key" "$name"
    fi
}

_emit_spec() {
    local num="$1"
    local name="$2"
    local cmd="$3"
    printf "%s|%s|%s\n" "$num" "$name" "$cmd"
}

get_window_specs() {
    _emit_spec 0 "infra" "$(_window_cmd infra infra "$(_cmd_infra)")"
    _emit_spec 1 "qdrant" "$(_window_cmd qdrant qdrant "$(_cmd_qdrant)")"
    _emit_spec 2 "backend" "$(_window_cmd backend backend "$(_cmd_backend)")"
    _emit_spec 3 "bff" "$(_window_cmd bff bff "$(_cmd_bff)")"
    _emit_spec 4 "auth" "$(_window_cmd auth auth "$(_cmd_auth)")"
    _emit_spec 5 "reco" "$(_window_cmd reco reco "$(_cmd_reco)")"
    _emit_spec 6 "ml" "$(_window_cmd ml ml "$(_cmd_ml)")"
    _emit_spec 7 "search" "$(_window_cmd search search "$(_cmd_search)")"
    _emit_spec 8 "frontend" "$(_window_cmd frontend frontend "$(_cmd_frontend)")"
    _emit_spec 9 "data" "$(_window_cmd data data "$(_cmd_data)")"
    _emit_spec 10 "monitoring" "$(_window_cmd monitoring monitoring "$(_cmd_monitoring)")"
}

get_required_ports() {
    local ports=()
    if is_enabled qdrant; then ports+=(6333 6334); fi
    if is_enabled backend; then ports+=(8000); fi
    if is_enabled bff; then ports+=(8001); fi
    if is_enabled reco; then ports+=(8002); fi
    if is_enabled auth; then ports+=(8003); fi
    if is_enabled ml; then ports+=(8004); fi
    if is_enabled search; then ports+=(8005); fi
    if is_enabled frontend; then ports+=(3000); fi
    printf "%s\n" "${ports[@]}"
}

python_services_enabled() {
    is_enabled backend || is_enabled bff || is_enabled auth || is_enabled reco || is_enabled ml || is_enabled search || is_enabled data
}

cleanup_existing_containers() {
    if ! is_enabled qdrant; then
        return 0
    fi
    echo -e "${YELLOW}🧹 Stopping any existing NextWatch containers...${NC}"
    docker stop nextwatch-qdrant 2>/dev/null || true
    docker rm nextwatch-qdrant 2>/dev/null || true
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
    local ports=("$@")
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

window_exists() {
    tmux_list_windows '#I' | grep -q "^$1$"
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

tmux_list_windows() {
    local format="${1:-#I:#W}"
    tmux list-windows -t "$SESSION" -F "$format" 2>/dev/null || true
}

send_window_cmd() {
    local window_num="$1"
    local window_name="$2"
    local window_cmd="$3"

    if [ -z "$window_cmd" ]; then
        return 0
    fi

    tmux_safe \
        "send command to window ${window_num} (${window_name})" \
        send-keys -t "$SESSION:$window_num" "PROJECT_ROOT=\"$PROJECT_ROOT\"; $window_cmd" C-m
}

add_window_if_missing() {
    local window_num=$1
    local window_name=$2
    local window_cmd=$3

    if window_exists "$window_num"; then
        echo -e "${GREEN}✅ Window ${window_num} (${window_name}) exists${NC}"
        return 0
    fi

    echo -e "${YELLOW}➕ Adding window ${window_num} (${window_name})${NC}"
    tmux_safe "create window ${window_num} (${window_name})" new-window -t "$SESSION:$window_num" -n "$window_name"
    send_window_cmd "$window_num" "$window_name" "$window_cmd"
    return 1
}

ensure_window_zero() {
    tmux_safe "set base-index" set-option -t "$SESSION" base-index 0
    tmux_safe "enable renumber-windows" set-option -t "$SESSION" renumber-windows on

    if ! window_exists 0; then
        first_window_num="$(tmux_list_windows '#I' | head -n 1)"
        tmux_safe "move first window to 0" move-window -s "$SESSION:$first_window_num" -t "$SESSION:0"
    fi
}

verify_expected_windows() {
    local expected_missing=0
    for expected in 0 1 2 3 4 5 6 7 8 9 10; do
        if ! window_exists "$expected"; then
            expected_missing=1
        fi
    done
    if [ "$expected_missing" -ne 0 ]; then
        echo -e "${RED}❌ Not all expected tmux windows (0-10) were created.${NC}" >&2
        tmux_list_windows '#I:#W' | sed 's/^/  /' >&2 || true
        exit 1
    fi
}

create_windows_from_specs() {
    while IFS='|' read -r window_num window_name window_cmd; do
        if [ "$window_num" = "0" ]; then
            tmux_safe "rename window 0" rename-window -t "$SESSION:0" "$window_name"
        else
            tmux_safe "create window ${window_num} (${window_name})" new-window -t "$SESSION:$window_num" -n "$window_name"
        fi
        send_window_cmd "$window_num" "$window_name" "$window_cmd"
    done < <(get_window_specs)
}

fix_missing_windows() {
    echo -e "${BLUE}🔧 Checking and fixing missing windows...${NC}"
    local windows_added=0

    # Only require Docker if we might actually start Qdrant.
    if is_enabled qdrant && ! window_exists 1; then
        check_docker_daemon
    fi

    while IFS='|' read -r window_num window_name window_cmd; do
        add_window_if_missing "$window_num" "$window_name" "$window_cmd" || ((windows_added++))
    done < <(get_window_specs)

    if [ $windows_added -eq 0 ]; then
        echo -e "${GREEN}✅ All windows are present!${NC}"
    else
        echo -e "${GREEN}✅ Added $windows_added missing windows!${NC}"
    fi
}

#
# -----------------------------------------------------------------------------
# Dependency checks (respect env toggles)
# -----------------------------------------------------------------------------
#
echo -e "${YELLOW}⚙️  Checking dependencies...${NC}"
require_cmd tmux "Install with Homebrew: brew install tmux"

if python_services_enabled; then
    require_cmd hatch "Install with pip: pip install hatch"
fi

if is_enabled frontend; then
    require_cmd pnpm "Install with Homebrew: brew install pnpm"
fi

if is_enabled qdrant; then
    require_cmd docker "Install Docker Desktop and ensure 'docker' is available on PATH"
fi

if is_enabled infra; then
    require_cmd redis-cli "Install Redis via Homebrew: brew install redis"
    require_cmd brew "This script expects Homebrew-managed Redis on macOS"
fi

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
            tmux_safe "attach session" attach -t "$SESSION"
            exit 0
            ;;
        2)
            echo -e "${YELLOW}Killing existing session...${NC}"
            tmux_safe "kill session" kill-session -t "$SESSION"
            ;;
        3)
            fix_missing_windows
            echo -e "${GREEN}Attaching to updated session...${NC}"
            tmux_safe "attach session" attach -t "$SESSION"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Attaching to existing session...${NC}"
            tmux_safe "attach session" attach -t "$SESSION"
            exit 0
            ;;
    esac
fi

echo -e "${GREEN}✅ Creating new tmux session '$SESSION'${NC}"

echo -e "${YELLOW}🔎 Running preflight checks...${NC}"
if is_enabled qdrant; then
    check_docker_daemon
fi
if is_enabled infra; then
    check_redis_ok_or_startable
fi

# Clean up any existing containers first
cleanup_existing_containers

# After cleanup, ensure remaining required ports are free.
REQUIRED_PORTS=()
while IFS= read -r port; do
    # Skip empty lines defensively
    if [ -n "$port" ]; then
        REQUIRED_PORTS+=("$port")
    fi
done < <(get_required_ports)

if [ "${#REQUIRED_PORTS[@]}" -gt 0 ]; then
    check_required_ports_available "${REQUIRED_PORTS[@]}"
fi

# Create the session and first window for infrastructure
tmux_safe "create tmux session" new-session -d -s "$SESSION" -n infra

ensure_window_zero

echo -e "${BLUE}🏗️ Creating tmux windows (0-10) and starting services...${NC}"
create_windows_from_specs
verify_expected_windows

# Go back to the infrastructure window (first window)
tmux_safe "select infra window" select-window -t "$SESSION:0"

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
tmux_safe "attach session" attach -t "$SESSION"
