***REMOVED***!/bin/bash

***REMOVED***
***REMOVED*** Next Watch - Git History Cleanup Script
***REMOVED***
***REMOVED*** This script removes all sensitive data from git history using BFG Repo-Cleaner
***REMOVED***
***REMOVED*** WARNING: This rewrites git history. Make sure you have a backup!
***REMOVED***
***REMOVED*** Prerequisites:
***REMOVED***   - Install BFG: brew install bfg
***REMOVED***   - Create backup of repository
***REMOVED***   - Ensure no uncommitted changes
***REMOVED***
***REMOVED***

set -e  ***REMOVED*** Exit on error

***REMOVED*** Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}Next Watch - Git History Cleanup${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""

***REMOVED*** Check if BFG is installed
if ! command -v bfg &> /dev/null; then
    echo -e "${RED}ERROR: BFG Repo-Cleaner is not installed${NC}"
    echo "Install with: brew install bfg"
    exit 1
fi

***REMOVED*** Check we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
    echo -e "${RED}ERROR: This script must be run from the repository root${NC}"
    exit 1
fi

***REMOVED*** Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}ERROR: You have uncommitted changes${NC}"
    echo "Please commit or stash your changes first"
    git status --short
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will rewrite git history!${NC}"
echo ""
echo "This script will:"
echo "  1. Create a backup of your repository"
echo "  2. Remove sensitive files from ALL commits"
echo "  3. Replace exposed credentials with placeholders"
echo "  4. Clean up git history"
echo ""
echo "Files/patterns to be removed:"
echo "  - All .env files (except .example files)"
echo "  - All .db files"  
echo "  - Specific sensitive configuration files"
echo ""
echo "Credentials to be redacted:"
echo "  - Grafana Cloud API keys"
echo "  - Passwords"
echo "  - Personal email and domain"
echo ""

read -p "Do you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Aborted."
    exit 1
fi

***REMOVED*** Step 1: Create backup
echo -e "${GREEN}Step 1: Creating backup...${NC}"
BACKUP_DIR="../next_watch_BACKUP_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"
echo ""

***REMOVED*** Step 2: Create passwords replacement file
echo -e "${GREEN}Step 2: Creating replacement patterns...${NC}"
cat > /tmp/nextwatch_passwords.txt << 'EOF'
glc_eyJvIjoiMTUwMjI5NSIsIm4iOiJzdGFjay0xMzM5NjgxLWFsbG95LW5leHR3YXRjaCIsImsiOiJCYzM0Sk5rOHEyUTA4aDRKb3M4MXU5UkkiLCJtIjp7InIiOiJwcm9kLWFwLXNvdXRoZWFzdC0xIn19==>YOUR_GRAFANA_API_KEY_HERE
NextWatch2024!Admin==>YOUR_ADMIN_PASSWORD_HERE  
NextWatch2024!Grafana==>YOUR_DB_PASSWORD_HERE
805656999857-a4ckp6k066aipeq52lkk1tm8h9ab908n==>YOUR_GOOGLE_CLIENT_ID
p.tran.alex@gmail.com==>contributors@example.com
alexsandbox.me==>your-domain.com
EOF
echo -e "${GREEN}✓ Replacement patterns created${NC}"
echo ""

***REMOVED*** Step 3: Clone as mirror for cleaning
echo -e "${GREEN}Step 3: Creating mirror clone for cleaning...${NC}"
MIRROR_DIR="../next_watch_clean_$(date +%Y%m%d_%H%M%S).git"
git clone --mirror . "$MIRROR_DIR"
cd "$MIRROR_DIR"
echo -e "${GREEN}✓ Mirror clone created${NC}"
echo ""

***REMOVED*** Step 4: Remove sensitive files
echo -e "${GREEN}Step 4: Removing sensitive files from history...${NC}"
echo "This may take a few minutes..."

***REMOVED*** Remove .env files
bfg --delete-files '.env' --no-blob-protection .
bfg --delete-files '.env.local' --no-blob-protection .
bfg --delete-files '.env.prod' --no-blob-protection .
bfg --delete-files '.env.monitoring.prod' --no-blob-protection .
bfg --delete-files '.env.observability.prod' --no-blob-protection .
bfg --delete-files '.env.development' --no-blob-protection .

***REMOVED*** Remove database files
bfg --delete-files 'movies.db' --no-blob-protection .
bfg --delete-files '*.db' --no-blob-protection .

echo -e "${GREEN}✓ Sensitive files removed${NC}"
echo ""

***REMOVED*** Step 5: Replace credentials
echo -e "${GREEN}Step 5: Replacing exposed credentials...${NC}"
bfg --replace-text /tmp/nextwatch_passwords.txt --no-blob-protection .
echo -e "${GREEN}✓ Credentials replaced${NC}"
echo ""

***REMOVED*** Step 6: Clean up
echo -e "${GREEN}Step 6: Cleaning up repository...${NC}"
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo -e "${GREEN}✓ Repository cleaned${NC}"
echo ""

***REMOVED*** Step 7: Return to original directory
cd - > /dev/null

echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}✓ Git history cleanup complete!${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. BACKUP CHECK:"
echo "   Your original repo is backed up at:"
echo "   $BACKUP_DIR"
echo ""
echo "2. REPLACE YOUR REPOSITORY:"
echo "   cd .."
echo "   mv next_watch next_watch_old"
echo "   git clone $MIRROR_DIR next_watch"
echo "   cd next_watch"
echo ""
echo "3. VERIFY THE CLEANUP:"
echo "   git log --all --oneline | head -20"
echo "   git log --all -- apps/auth-api/.env"
echo ""
echo "4. PUSH TO REMOTE (FORCE PUSH - CAREFUL!):"
echo "   git remote add origin <your-repo-url>"
echo "   git push --force --all"
echo "   git push --force --tags"
echo ""
echo "5. IMMEDIATELY AFTER PUSHING:"
echo "   ⚠️  REVOKE ALL EXPOSED CREDENTIALS:"
echo "   - Grafana Cloud API keys (https://grafana.com)"
echo "   - Change Grafana admin password"
echo "   - Rotate JWT secrets"
echo "   - Rotate internal API keys"
echo ""
echo -e "${RED}IMPORTANT: Anyone who has cloned the repo must re-clone!${NC}"
echo ""

