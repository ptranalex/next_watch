***REMOVED***!/usr/bin/env bash
***REMOVED*** File: start_services_tmux.sh
***REMOVED*** Start all Next Watch services locally within tmux

set -e

SESSION="nextwatch"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

***REMOVED*** Cleanup function to stop any existing containers
cleanup_existing_containers() {
    echo -e "${YELLOW}🧹 Stopping any existing NextWatch containers...${NC}"
    ***REMOVED*** Only stop Qdrant container, keep Redis as Homebrew service
    docker stop nextwatch-qdrant 2>/dev/null || true
    docker rm nextwatch-qdrant 2>/dev/null || true
}

***REMOVED*** Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${BLUE}🚀 Starting Next Watch Services...${NC}"
echo -e "${CYAN}Project root: ${PROJECT_ROOT}${NC}"

***REMOVED*** Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

***REMOVED*** Check dependencies
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

***REMOVED*** Function to check if a window exists
window_exists() {
    tmux list-windows -t $SESSION -F '***REMOVED***I' 2>/dev/null | grep -q "^$1$"
}

***REMOVED*** Function to add a window if it doesn't exist
add_window_if_missing() {
    local window_num=$1
    local window_name=$2
    local window_cmd=$3
    
    if window_exists $window_num; then
        echo -e "${GREEN}✅ Window $window_num ($window_name) exists${NC}"
        return 0
    else
        echo -e "${YELLOW}➕ Adding window $window_num ($window_name)${NC}"
        tmux new-window -t $SESSION:$window_num -n $window_name
        if [ -n "$window_cmd" ]; then
            tmux send-keys -t $SESSION:$window_name "$window_cmd" C-m
        fi
        return 1
    fi
}

***REMOVED*** Function to fix missing windows
fix_missing_windows() {
    echo -e "${BLUE}🔧 Checking and fixing missing windows...${NC}"
    local windows_added=0
    
    ***REMOVED*** Check all expected windows and add missing ones
    add_window_if_missing 0 "infra" "echo '🔴 Redis Infrastructure' && redis-cli ping 2>/dev/null && echo '✅ Redis responding' || echo '❌ Redis not responding'" || ((windows_added++))
    add_window_if_missing 1 "qdrant" "echo '🟠 Starting Qdrant...' && mkdir -p ${PROJECT_ROOT}/data/qdrant_storage && docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v ${PROJECT_ROOT}/data/qdrant_storage:/qdrant/storage qdrant/qdrant" || ((windows_added++))
    add_window_if_missing 2 "backend" "cd ${PROJECT_ROOT}/apps/backend-api && echo '🔧 Starting Backend API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 3 "bff" "cd ${PROJECT_ROOT}/apps/bff-api && echo '🌐 Starting BFF API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 4 "auth" "cd ${PROJECT_ROOT}/apps/auth-api && echo '🔐 Starting Auth API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 5 "reco" "cd ${PROJECT_ROOT}/apps/recommendation-api && echo '🤖 Starting Recommendation API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 6 "ml" "cd ${PROJECT_ROOT}/apps/ml-api && echo '🧠 Starting ML API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 7 "search" "cd ${PROJECT_ROOT}/apps/search-api && echo '🔍 Starting Search API...' && hatch run install-libs && hatch run dev" || ((windows_added++))
    add_window_if_missing 8 "frontend" "cd ${PROJECT_ROOT}/apps/web-nextjs && echo '🎨 Starting Frontend...' && pnpm install && pnpm dev" || ((windows_added++))
    add_window_if_missing 9 "data" "cd ${PROJECT_ROOT}/apps/data-importer && echo '📊 Data Importer ready. Use: hatch run cli sync movies --help'" || ((windows_added++))
    add_window_if_missing 10 "monitoring" "cd ${PROJECT_ROOT} && echo '📈 Monitoring ready. Run ./infra/scripts/check-services.sh to check status'" || ((windows_added++))
    
    if [ $windows_added -eq 0 ]; then
        echo -e "${GREEN}✅ All windows are present!${NC}"
    else
        echo -e "${GREEN}✅ Added $windows_added missing windows!${NC}"
    fi
}

***REMOVED*** Handle existing session
if tmux has-session -t $SESSION 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Session '$SESSION' already exists.${NC}"
    echo -e "${BLUE}Choose an option:${NC}"
    echo -e "  1. Attach to existing session"
    echo -e "  2. Kill and recreate session"
    echo -e "  3. Fix missing windows in existing session"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo -e "${GREEN}Attaching to existing session...${NC}"
            tmux attach -t $SESSION
            exit 0
            ;;
        2)
            echo -e "${YELLOW}Killing existing session...${NC}"
            tmux kill-session -t $SESSION
            ;;
        3)
            fix_missing_windows
            echo -e "${GREEN}Attaching to updated session...${NC}"
            tmux attach -t $SESSION
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Attaching to existing session...${NC}"
            tmux attach -t $SESSION
            exit 0
            ;;
    esac
fi

echo -e "${GREEN}✅ Creating new tmux session '$SESSION'${NC}"

***REMOVED*** Clean up any existing containers first
cleanup_existing_containers

***REMOVED*** Create the session and first window for infrastructure
tmux new-session -d -s $SESSION -n infra

***REMOVED*** Set the base index for windows to 0 (default, but explicit)
tmux set-option -t $SESSION base-index 0

***REMOVED*** Set up infrastructure services first (Redis Homebrew + Qdrant Docker)
echo -e "${BLUE}🏗️ Setting up infrastructure services...${NC}"

***REMOVED*** Check and start Redis via Homebrew if needed
tmux send-keys -t $SESSION:infra "echo '🔄 Checking Redis (Homebrew) service...'" C-m
tmux send-keys -t $SESSION:infra "if ! redis-cli ping >/dev/null 2>&1; then" C-m
tmux send-keys -t $SESSION:infra "  echo '🚀 Starting Redis via Homebrew...'" C-m
tmux send-keys -t $SESSION:infra "  brew services start redis" C-m
tmux send-keys -t $SESSION:infra "  sleep 2" C-m
tmux send-keys -t $SESSION:infra "else" C-m
tmux send-keys -t $SESSION:infra "  echo '✅ Redis already running'" C-m
tmux send-keys -t $SESSION:infra "fi" C-m

***REMOVED*** Show infrastructure status
tmux send-keys -t $SESSION:infra "echo '🔍 Infrastructure Status:'" C-m
tmux send-keys -t $SESSION:infra "echo '🔴 Redis (Homebrew):' && redis-cli ping 2>/dev/null && echo '  ✅ Redis responding on localhost:6379' || echo '  ❌ Redis not responding'" C-m
tmux send-keys -t $SESSION:infra "sleep 2" C-m

***REMOVED*** Window 2: Qdrant (dedicated window with logs)
echo -e "${BLUE}🟠 Setting up Qdrant...${NC}"
tmux new-window -t $SESSION -n qdrant
tmux send-keys -t $SESSION:qdrant "echo '🔄 Starting Qdrant container with persistent storage...'" C-m
tmux send-keys -t $SESSION:qdrant "mkdir -p ${PROJECT_ROOT}/data/qdrant_storage && echo '📁 Storage directory ready'" C-m
tmux send-keys -t $SESSION:qdrant "docker run --rm --name nextwatch-qdrant -p 6333:6333 -p 6334:6334 -v ${PROJECT_ROOT}/data/qdrant_storage:/qdrant/storage qdrant/qdrant" C-m

***REMOVED*** Window 3: Backend API (port 8000)
echo -e "${BLUE}🔧 Setting up Backend API...${NC}"
tmux new-window -t $SESSION -n backend
tmux send-keys -t $SESSION:backend "cd ${PROJECT_ROOT}/apps/backend-api" C-m
tmux send-keys -t $SESSION:backend "echo '🔄 Starting Backend API on port 8000...'" C-m
tmux send-keys -t $SESSION:backend "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 4: BFF API (port 8001)
echo -e "${BLUE}🌐 Setting up BFF API...${NC}"
tmux new-window -t $SESSION -n bff
tmux send-keys -t $SESSION:bff "cd ${PROJECT_ROOT}/apps/bff-api" C-m
tmux send-keys -t $SESSION:bff "echo '🔄 Starting BFF API on port 8001...'" C-m
tmux send-keys -t $SESSION:bff "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 5: Auth API (port 8003)
echo -e "${BLUE}🔐 Setting up Auth API...${NC}"
tmux new-window -t $SESSION -n auth
tmux send-keys -t $SESSION:auth "cd ${PROJECT_ROOT}/apps/auth-api" C-m
tmux send-keys -t $SESSION:auth "echo '🔄 Starting Auth API on port 8003...'" C-m
tmux send-keys -t $SESSION:auth "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 6: Recommendation API (port 8002)
echo -e "${BLUE}🤖 Setting up Recommendation API...${NC}"
tmux new-window -t $SESSION -n reco
tmux send-keys -t $SESSION:reco "cd ${PROJECT_ROOT}/apps/recommendation-api" C-m
tmux send-keys -t $SESSION:reco "echo '🔄 Starting Recommendation API on port 8002...'" C-m
tmux send-keys -t $SESSION:reco "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 7: ML API (port 8004)
echo -e "${BLUE}🧠 Setting up ML API...${NC}"
tmux new-window -t $SESSION -n ml
tmux send-keys -t $SESSION:ml "cd ${PROJECT_ROOT}/apps/ml-api" C-m
tmux send-keys -t $SESSION:ml "echo '🔄 Starting ML API on port 8004...'" C-m
tmux send-keys -t $SESSION:ml "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 8: Search API (port 8005)
echo -e "${BLUE}🔍 Setting up Search API...${NC}"
tmux new-window -t $SESSION -n search
tmux send-keys -t $SESSION:search "cd ${PROJECT_ROOT}/apps/search-api" C-m
tmux send-keys -t $SESSION:search "echo '🔄 Starting Search API on port 8005...'" C-m
tmux send-keys -t $SESSION:search "hatch run install-libs && hatch run dev" C-m

***REMOVED*** Window 9: Frontend (Next.js on port 3000)
echo -e "${BLUE}🎨 Setting up frontend...${NC}"
tmux new-window -t $SESSION -n frontend
tmux send-keys -t $SESSION:frontend "cd ${PROJECT_ROOT}/apps/web-nextjs" C-m
tmux send-keys -t $SESSION:frontend "echo '🔄 Starting Next.js Frontend on port 3000...'" C-m
tmux send-keys -t $SESSION:frontend "pnpm install && pnpm dev" C-m

***REMOVED*** Window 10: Data & Utilities
echo -e "${BLUE}📊 Setting up data & utilities...${NC}"
tmux new-window -t $SESSION -n data
tmux send-keys -t $SESSION:data "cd ${PROJECT_ROOT}/apps/data-importer" C-m
tmux send-keys -t $SESSION:data "echo '📥 Data Importer ready. Use: hatch run cli sync movies --help'" C-m

***REMOVED*** Window 11: Monitoring
echo -e "${BLUE}📈 Setting up monitoring...${NC}"
tmux new-window -t $SESSION -n monitoring
tmux send-keys -t $SESSION:monitoring "cd ${PROJECT_ROOT}" C-m
tmux send-keys -t $SESSION:monitoring "echo '🔍 Service status checker ready'" C-m

***REMOVED*** Go back to the infrastructure window (first window)
tmux select-window -t $SESSION:infra

***REMOVED*** Point to the static check-services.sh script
tmux send-keys -t $SESSION:monitoring "echo 'Use ./infra/scripts/check-services.sh to check all service status'" C-m

***REMOVED*** Display helpful information
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

***REMOVED*** Attach to the session
tmux attach -t $SESSION
