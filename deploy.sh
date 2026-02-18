#!/bin/bash

# 24/7 Deployment Setup Script
# This script automates the entire deployment process

set -e  # Exit on error

echo "======================================================================"
echo "🤖 UAE Investor Research Agent - 24/7 Deployment Setup"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi
print_success "Git installed"

# Check GitHub CLI (optional but recommended)
if command -v gh &> /dev/null; then
    print_success "GitHub CLI installed"
    HAS_GH_CLI=true
else
    print_info "GitHub CLI not found (optional - you can set up secrets manually)"
    HAS_GH_CLI=false
fi

echo ""
echo "======================================================================"
echo "📋 Setup Configuration"
echo "======================================================================"
echo ""

# Get user input
read -p "Repository name (default: uae-investor-agent): " REPO_NAME
REPO_NAME=${REPO_NAME:-uae-investor-agent}

read -p "Make repository private? (y/n, default: n): " IS_PRIVATE
if [[ "$IS_PRIVATE" =~ ^[Yy]$ ]]; then
    VISIBILITY="--private"
else
    VISIBILITY="--public"
fi

echo ""
read -p "Enter your Anthropic API key: " ANTHROPIC_KEY
if [ -z "$ANTHROPIC_KEY" ]; then
    print_error "API key is required!"
    exit 1
fi

echo ""
read -p "Do you want to enable Google Sheets sync? (y/n): " ENABLE_SHEETS
if [[ "$ENABLE_SHEETS" =~ ^[Yy]$ ]]; then
    echo ""
    print_info "You'll need to:"
    echo "  1. Create a Google Cloud service account"
    echo "  2. Enable Google Sheets API"
    echo "  3. Download the JSON credentials file"
    echo ""
    read -p "Path to your Google service account JSON file: " SHEETS_CREDS_PATH
    
    if [ ! -f "$SHEETS_CREDS_PATH" ]; then
        print_error "Credentials file not found!"
        exit 1
    fi
    
    SHEETS_CREDS=$(cat "$SHEETS_CREDS_PATH")
fi

echo ""
read -p "Enable Slack notifications? (y/n): " ENABLE_SLACK
if [[ "$ENABLE_SLACK" =~ ^[Yy]$ ]]; then
    read -p "Enter your Slack webhook URL: " SLACK_WEBHOOK
fi

echo ""
echo "======================================================================"
echo "🚀 Deploying to GitHub"
echo "======================================================================"
echo ""

# Initialize Git if not already
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    git branch -M main
    print_success "Git repository initialized"
fi

# Add all files
print_info "Adding files to repository..."
git add .
git commit -m "Initial commit: UAE Investor Research Agent" || print_info "No changes to commit"
print_success "Files added"

# Create GitHub repository
if [ "$HAS_GH_CLI" = true ]; then
    print_info "Creating GitHub repository..."
    
    if gh repo view "$REPO_NAME" &> /dev/null; then
        print_info "Repository already exists, skipping creation"
    else
        gh repo create "$REPO_NAME" $VISIBILITY --source=. --push
        print_success "Repository created and pushed"
    fi
    
    # Set up secrets
    echo ""
    print_info "Setting up GitHub secrets..."
    
    gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_KEY"
    print_success "ANTHROPIC_API_KEY secret added"
    
    if [[ "$ENABLE_SHEETS" =~ ^[Yy]$ ]]; then
        gh secret set GSHEET_CREDENTIALS --body "$SHEETS_CREDS"
        print_success "GSHEET_CREDENTIALS secret added"
    fi
    
    if [[ "$ENABLE_SLACK" =~ ^[Yy]$ ]]; then
        gh secret set SLACK_WEBHOOK_URL --body "$SLACK_WEBHOOK"
        print_success "SLACK_WEBHOOK_URL secret added"
    fi
    
else
    print_info "GitHub CLI not available. Please:"
    echo ""
    echo "1. Create a new repository on GitHub: https://github.com/new"
    echo "   Name: $REPO_NAME"
    echo "   Visibility: $([ -n "$VISIBILITY" ] && echo "Private" || echo "Public")"
    echo ""
    echo "2. Add this remote and push:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. Add secrets in GitHub:"
    echo "   Settings → Secrets and variables → Actions → New repository secret"
    echo ""
    echo "   Required secrets:"
    echo "   - ANTHROPIC_API_KEY: $ANTHROPIC_KEY"
    
    if [[ "$ENABLE_SHEETS" =~ ^[Yy]$ ]]; then
        echo "   - GSHEET_CREDENTIALS: (paste your service account JSON)"
    fi
    
    if [[ "$ENABLE_SLACK" =~ ^[Yy]$ ]]; then
        echo "   - SLACK_WEBHOOK_URL: $SLACK_WEBHOOK"
    fi
    echo ""
    
    read -p "Press Enter when you've completed these steps..."
fi

echo ""
echo "======================================================================"
echo "⚙️  Configuring Workflow"
echo "======================================================================"
echo ""

# Update workflow schedule if needed
read -p "How often should the agent run? (hours, default: 6): " RUN_FREQUENCY
RUN_FREQUENCY=${RUN_FREQUENCY:-6}

print_info "Updating workflow schedule to run every $RUN_FREQUENCY hours..."

# Update cron expression in workflow file
sed -i "s/0 \*\/6 \* \* \*/0 *\/$RUN_FREQUENCY * * */g" .github/workflows/investor-research.yml

git add .github/workflows/investor-research.yml
git commit -m "Update workflow frequency to $RUN_FREQUENCY hours" || true
git push || print_info "Push manually after setup"

print_success "Workflow configured"

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "Your agent is now running 24/7! 🎉"
echo ""
echo "📊 What happens next:"
echo "   • Agent runs automatically every $RUN_FREQUENCY hours"
echo "   • Results are committed to your GitHub repository"

if [[ "$ENABLE_SHEETS" =~ ^[Yy]$ ]]; then
    echo "   • Google Sheets is updated with new investors"
fi

if [[ "$ENABLE_SLACK" =~ ^[Yy]$ ]]; then
    echo "   • Slack notifications sent after each run"
fi

echo ""
echo "🔗 Quick Links:"
if [ "$HAS_GH_CLI" = true ]; then
    REPO_URL=$(gh repo view --json url -q .url)
    echo "   Repository: $REPO_URL"
    echo "   Actions: $REPO_URL/actions"
    echo "   Settings: $REPO_URL/settings/secrets/actions"
else
    echo "   Repository: https://github.com/YOUR_USERNAME/$REPO_NAME"
    echo "   Actions: https://github.com/YOUR_USERNAME/$REPO_NAME/actions"
fi

echo ""
echo "💡 Next Steps:"
echo "   1. Visit the Actions tab to see your first run"
echo "   2. Click 'Run workflow' to trigger manually"
echo "   3. Check the CSV file in your repository after run completes"

if [[ "$ENABLE_SHEETS" =~ ^[Yy]$ ]]; then
    echo "   4. Share your Google Sheet with team members"
fi

echo ""
echo "📚 Documentation:"
echo "   • README.md - Full usage guide"
echo "   • DEPLOYMENT_GUIDE.md - Advanced deployment options"
echo ""
echo "🎯 Happy fundraising! Good luck with Matchr!"
echo ""
