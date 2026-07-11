#!/bin/bash

# Default Branch Migration Script
# This script helps migrate from "Main" to "main" branch

set -e  # Exit on error

echo "🔄 Barrot-Agent Default Branch Migration Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository. Please run this script from the repository root."
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Check remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "none")
print_info "Remote URL: $REMOTE_URL"

# Extract GitHub repo path (handles both HTTPS and SSH URLs)
REPO_PATH=""
if [[ $REMOTE_URL == https://github.com/* ]]; then
    REPO_PATH=$(echo "$REMOTE_URL" | sed 's|https://github.com/||' | sed 's|\.git$||')
elif [[ $REMOTE_URL == git@github.com:* ]]; then
    REPO_PATH=$(echo "$REMOTE_URL" | sed 's|git@github.com:||' | sed 's|\.git$||')
fi

if [ -z "$REPO_PATH" ]; then
    print_warning "Could not extract GitHub repository path from remote URL"
    SETTINGS_URL="<your-repo-settings-url>"
    PULLS_URL="<your-repo-pulls-url>"
else
    SETTINGS_URL="https://github.com/${REPO_PATH}/settings/branches"
    PULLS_URL="https://github.com/${REPO_PATH}/pulls"
fi

echo ""
echo "This script will help you migrate from 'Main' to 'main' branch."
echo ""

# Fetch latest changes
print_info "Fetching latest changes from origin..."
git fetch origin

# Check if Main branch exists on remote
if git ls-remote --heads origin Main | grep -q Main; then
    print_success "Found 'Main' branch on remote"
    
    # Checkout Main branch
    print_info "Checking out 'Main' branch..."
    git checkout Main
    
    # Pull latest changes
    print_info "Pulling latest changes..."
    git pull origin Main
    
    # Create main branch
    print_info "Creating 'main' branch from 'Main'..."
    if git show-ref --verify --quiet refs/heads/main; then
        print_info "'main' branch already exists locally, switching to it..."
        git checkout main
    else
        git checkout -b main
        print_success "Created new 'main' branch"
    fi
    
    # Push to origin
    print_info "Pushing 'main' branch to origin..."
    git push origin main
    
    print_success "Successfully created and pushed 'main' branch!"
    echo ""
    
else
    print_warning "'Main' branch not found on remote"
    
    # Check if main already exists
    if git ls-remote --heads origin main | grep -q main; then
        print_info "'main' branch already exists on remote"
        print_info "Checking out 'main' branch..."
        git checkout main
        git pull origin main
        print_success "Switched to 'main' branch"
    else
        print_error "Neither 'Main' nor 'main' branch found on remote"
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "📝 Next Steps (Manual Actions Required):"
echo "================================================"
echo ""
echo "1. 🌐 Change Default Branch in GitHub:"
echo "   - Go to: $SETTINGS_URL"
echo "   - Click the switch icon next to 'Main' in Default branch section"
echo "   - Select 'main' from dropdown"
echo "   - Click 'Update' and confirm"
echo ""
echo "2. 🛡️  Update Branch Protection Rules:"
echo "   - Go to: $SETTINGS_URL"
echo "   - Configure protection rules for 'main' branch"
echo "   - Remove protection from 'Main' if desired"
echo ""
echo "3. 🔀 Update Open Pull Requests:"
echo "   - Retarget all PRs from 'Main' to 'main'"
echo "   - Go to: $PULLS_URL"
echo ""
echo "4. 📢 Notify Contributors:"
echo "   - Inform team about the default branch change"
echo "   - Share contributor instructions from DEFAULT_BRANCH_GUIDE.md"
echo ""
echo "5. 🗑️  Delete Old Branch (Optional):"
echo "   - After confirming everything works"
echo "   - Run: git push origin --delete Main"
echo ""
echo "================================================"
echo "For Contributors to Update Their Local Repository:"
echo "================================================"
echo ""
echo "git fetch origin"
echo "git checkout main"
echo "git branch -u origin/main"
echo "git pull"
echo "git branch -D Main  # Optional: remove old local branch"
echo ""
print_success "Migration script completed successfully!"
echo ""
print_info "See DEFAULT_BRANCH_GUIDE.md for detailed instructions"
