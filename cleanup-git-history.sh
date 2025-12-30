#!/bin/bash

#
# Next Watch - Git History Cleanup Script
#
# This script removes all sensitive data from git history using BFG Repo-Cleaner
#
# WARNING: This rewrites git history. Make sure you have a backup!
#
# Prerequisites:
#   - Install BFG: brew install bfg
#   - Create backup of repository
#   - Ensure no uncommitted changes
#
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}Next Watch - Git History Cleanup${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""

# Check if BFG is installed
if ! command -v bfg &> /dev/null; then
    echo -e "${RED}ERROR: BFG Repo-Cleaner is not installed${NC}"
    echo "Install with: brew install bfg"
    exit 1
fi

# Check we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
    echo -e "${RED}ERROR: This script must be run from the repository root${NC}"
    exit 1
fi

# Check for uncommitted changes
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
echo "  - Any .secrets file"
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

# Step 1: Create backup
echo -e "${GREEN}Step 1: Creating backup...${NC}"
BACKUP_DIR="../next_watch_BACKUP_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"
echo ""

# Step 2: Prepare replacement patterns (NO REAL SECRETS IN REPO)
#
# IMPORTANT:
# - Never store real secrets in this repository (even inside this cleanup script).
# - Provide your own replacements file when running this script, e.g.:
#     ./cleanup-git-history.sh /path/to/replacements.txt
#
# BFG replacement file format:
#   <literal-to-find>==><replacement>
#
echo -e "${GREEN}Step 2: Preparing replacement patterns...${NC}"
REPLACEMENTS_FILE="${1:-/tmp/nextwatch_replacements.txt}"

if [ ! -f "$REPLACEMENTS_FILE" ]; then
    cat > "$REPLACEMENTS_FILE" << 'EOF'
#
#
#
#
#
#
# Examples (edit/remove as needed):
# my_old_api_key_value==>REDACTED_API_KEY
# my_old_password==>REDACTED_PASSWORD
# my-domain.example==>your-domain.com
# someone@example.com==>contributors@example.com
EOF
    echo -e "${YELLOW}⚠️  Replacement file not found; created a TEMPLATE at:${NC} $REPLACEMENTS_FILE"
    echo -e "${YELLOW}   Edit it to include the exact literals you need to scrub, then re-run the script.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Using replacements file:${NC} $REPLACEMENTS_FILE"
echo ""

# Step 3: Clone as mirror for cleaning
echo -e "${GREEN}Step 3: Creating mirror clone for cleaning...${NC}"
MIRROR_DIR="../next_watch_clean_$(date +%Y%m%d_%H%M%S).git"
git clone --mirror . "$MIRROR_DIR"
cd "$MIRROR_DIR"
echo -e "${GREEN}✓ Mirror clone created${NC}"
echo ""

# Step 4: Remove sensitive files
echo -e "${GREEN}Step 4: Removing sensitive files from history...${NC}"
echo "This may take a few minutes..."

# Remove explicit secrets files
bfg --delete-files '.secrets' --no-blob-protection .

# Remove .env files
bfg --delete-files '.env' --no-blob-protection .
bfg --delete-files '.env.local' --no-blob-protection .
bfg --delete-files '.env.prod' --no-blob-protection .
bfg --delete-files '.env.production' --no-blob-protection .
bfg --delete-files '.env.monitoring' --no-blob-protection .
bfg --delete-files '.env.monitoring.prod' --no-blob-protection .
bfg --delete-files '.env.observability.prod' --no-blob-protection .
bfg --delete-files '.env.development' --no-blob-protection .

# Remove database files
bfg --delete-files 'movies.db' --no-blob-protection .
bfg --delete-files '*.db' --no-blob-protection .

echo -e "${GREEN}✓ Sensitive files removed${NC}"
echo ""

# Step 5: Replace credentials
echo -e "${GREEN}Step 5: Replacing exposed credentials...${NC}"
bfg --replace-text "$REPLACEMENTS_FILE" --no-blob-protection .
echo -e "${GREEN}✓ Credentials replaced${NC}"
echo ""

# Step 6: Clean up
echo -e "${GREEN}Step 6: Cleaning up repository...${NC}"
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo -e "${GREEN}✓ Repository cleaned${NC}"
echo ""

# Step 7: Return to original directory
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
