#!/bin/bash

echo "🚀 Starting RazorFlow AI Local Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env from .env.local template...${NC}"
    cp .env.local .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
fi

# Setup backend
echo -e "\n${BLUE}🔧 Setting up backend...${NC}"
cd backend || exit

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📥 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Go back to root
cd ..

# Setup frontend
echo -e "\n${BLUE}🔧 Setting up frontend...${NC}"
cd frontend || exit

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📥 Installing Node.js dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}✅ Node.js dependencies already installed${NC}"
fi

# Go back to root
cd ..

echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "${BLUE}To start the application:${NC}"
echo -e "  1. Backend: ${YELLOW}./start-backend.sh${NC}"
echo -e "  2. Frontend: ${YELLOW}./start-frontend.sh${NC}"
echo -e "  3. Both: ${YELLOW}./start-local.sh${NC}"
echo -e "\n${BLUE}To run tests:${NC}"
echo -e "  - All tests: ${YELLOW}./run-tests.sh${NC}"
echo -e "  - Playwright only: ${YELLOW}./run-playwright.sh${NC}"
