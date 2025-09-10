#!/bin/bash

echo "🎭 Running Playwright Tests"
echo "==========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if servers are running
check_server() {
    local url=$1
    local name=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not running${NC}"
        return 1
    fi
}

# Function to start servers if needed
start_servers() {
    echo -e "${YELLOW}🚀 Starting servers for testing...${NC}"
    
    # Start backend
    ./start-backend.sh &
    BACKEND_PID=$!
    
    # Start frontend  
    ./start-frontend.sh &
    FRONTEND_PID=$!
    
    # Wait for servers to start
    echo -e "${YELLOW}⏳ Waiting for servers to start...${NC}"
    sleep 10
    
    # Check if servers are ready
    local backend_ready=false
    local frontend_ready=false
    
    for i in {1..30}; do
        if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
            backend_ready=true
        fi
        
        if curl -s "http://localhost:5173" > /dev/null 2>&1; then
            frontend_ready=true
        fi
        
        if $backend_ready && $frontend_ready; then
            echo -e "${GREEN}✅ Both servers are ready!${NC}"
            break
        fi
        
        echo -e "${YELLOW}⏳ Waiting... (${i}/30)${NC}"
        sleep 2
    done
    
    if ! $backend_ready || ! $frontend_ready; then
        echo -e "${RED}❌ Servers failed to start properly${NC}"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 1
    fi
}

# Function to cleanup
cleanup() {
    if [ ! -z "$BACKEND_PID" ] && [ ! -z "$FRONTEND_PID" ]; then
        echo -e "\n${YELLOW}🛑 Stopping test servers...${NC}"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        wait
        echo -e "${GREEN}✅ Test servers stopped${NC}"
    fi
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM EXIT

# Check if servers are already running
echo -e "${BLUE}🔍 Checking if servers are running...${NC}"

backend_running=$(check_server "http://localhost:8000/health" "Backend")
frontend_running=$(check_server "http://localhost:5173" "Frontend")

# Start servers if not running
if ! $backend_running || ! $frontend_running; then
    start_servers
fi

# Activate test environment
echo -e "\n${BLUE}🧪 Preparing test environment...${NC}"
if [ -d "test-env" ]; then
    source test-env/bin/activate
    echo -e "${GREEN}✅ Test environment activated${NC}"
else
    echo -e "${RED}❌ Test environment not found. Run tests/setup_test_env.sh first${NC}"
    exit 1
fi

# Run Playwright tests
echo -e "\n${BLUE}🎭 Running Playwright tests...${NC}"
echo -e "${YELLOW}📊 Test results will be available in playwright-report/${NC}"

cd tests || exit
pytest test_e2e_playwright.py -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All Playwright tests passed!${NC}"
else
    echo -e "\n${RED}❌ Some Playwright tests failed${NC}"
    echo -e "${YELLOW}📊 Check the detailed report in playwright-report/${NC}"
fi

# Show report location
echo -e "\n${BLUE}📊 Test Reports:${NC}"
echo -e "  • Playwright HTML Report: ${YELLOW}file://$(pwd)/playwright-report/index.html${NC}"
echo -e "  • Screenshots: ${YELLOW}$(pwd)/test-results/${NC}"
