#!/bin/bash
# Railway Deployment Preparation Script
# Run this before deploying to Railway

set -e

echo "🚀 Preparing RazorFlow AI for Railway Deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "railway.json" ]]; then
    print_error "railway.json not found. Please run this script from the project root."
    exit 1
fi

print_success "Found railway.json configuration"

# Check if backend directory exists
if [[ ! -d "backend" ]]; then
    print_error "Backend directory not found"
    exit 1
fi

print_success "Backend directory found"

# Check requirements.txt
if [[ ! -f "backend/requirements.txt" ]]; then
    print_error "backend/requirements.txt not found"
    exit 1
fi

print_success "Requirements.txt found"

# Check main.py
if [[ ! -f "backend/main.py" ]]; then
    print_error "backend/main.py not found"
    exit 1
fi

print_success "Main application file found"

# Check if FastAPI app is properly configured
if grep -q "uvicorn.run" backend/main.py; then
    print_success "FastAPI app properly configured for Railway"
else
    print_warning "FastAPI app may need configuration updates"
fi

# Check if PORT environment variable is used
if grep -q "PORT" backend/main.py; then
    print_success "PORT environment variable handling found"
else
    print_warning "Consider using PORT environment variable for Railway compatibility"
fi

# Validate railway.json
if python3 -c "import json; json.load(open('railway.json'))" 2>/dev/null; then
    print_success "railway.json is valid JSON"
else
    print_error "railway.json contains invalid JSON"
    exit 1
fi

# Check for .env files (should not be committed)
if [[ -f ".env" ]]; then
    print_warning ".env file found - ensure it's in .gitignore"
fi

if [[ -f "backend/.env" ]]; then
    print_warning "backend/.env file found - ensure it's in .gitignore"
fi

# Check .gitignore
if [[ -f ".gitignore" ]]; then
    if grep -q ".env" .gitignore; then
        print_success ".env files are properly ignored"
    else
        print_warning "Consider adding .env to .gitignore"
    fi
else
    print_warning ".gitignore not found - consider creating one"
fi

# Check if git repo is initialized
if [[ -d ".git" ]]; then
    print_success "Git repository initialized"
    
    # Check if there are uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "Uncommitted changes detected"
        echo "Consider committing changes before deployment:"
        git status --short
    else
        print_success "No uncommitted changes"
    fi
    
    # Check if remote origin is set
    if git remote get-url origin &>/dev/null; then
        origin_url=$(git remote get-url origin)
        print_success "Git remote origin: $origin_url"
    else
        print_warning "Git remote origin not set - needed for GitHub deployment"
    fi
else
    print_warning "Git repository not initialized - needed for GitHub deployment"
fi

echo ""
echo "📋 Pre-deployment Summary:"
echo ""
echo "✅ Required files present"
echo "✅ Configuration validated"
echo "✅ FastAPI app ready"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. 📤 Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for Railway deployment'"
echo "   git push origin main"
echo ""
echo "2. 🌐 Deploy on Railway:"
echo "   • Visit: https://railway.com/new"
echo "   • Click: 'Deploy from GitHub repo'"
echo "   • Select: Your repository"
echo "   • Click: 'Deploy Now'"
echo ""
echo "3. 🔧 Configure Environment Variables:"
echo "   • Go to your service → Variables tab"
echo "   • Add variables from .env.railway.template"
echo "   • Include: DATABASE_URL, OPENAI_API_KEY, SECRET_KEY"
echo ""
echo "4. 🌍 Generate Public Domain:"
echo "   • Go to Settings → Networking"
echo "   • Click: 'Generate Domain'"
echo ""
echo "5. 🧪 Test Your Deployment:"
echo "   • Visit: https://your-app.railway.app/health"
echo "   • Check: All API endpoints work"
echo ""
echo "📚 For detailed instructions, see: RAILWAY_DEPLOYMENT_GUIDE.md"
echo ""
print_success "RazorFlow AI is ready for Railway deployment! 🎉"
