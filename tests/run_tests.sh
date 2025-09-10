#!/bin/bash

# RazorFlow AI Test Framework
# ===========================
# Main test runner script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$TEST_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORTS_DIR="$TEST_DIR/reports"

echo -e "${BLUE}🧪 RazorFlow AI Test Framework${NC}"
echo "=================================="

# Parse command line arguments
TEST_TYPE="all"
VERBOSE=""
COVERAGE=""
DEPLOYMENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov"
            shift
            ;;
        -d|--deployment)
            DEPLOYMENT="true"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE     Test type: unit, integration, e2e, deployment, all"
            echo "  -v, --verbose       Verbose output"
            echo "  -c, --coverage      Generate coverage report"
            echo "  -d, --deployment    Run deployment tests"
            echo "  -h, --help          Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                      # Run all tests"
            echo "  $0 -t unit -v           # Run unit tests with verbose output"
            echo "  $0 -t deployment -d     # Run deployment tests"
            echo "  $0 -c                   # Run with coverage"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run tests
run_tests() {
    local test_path="$1"
    local test_name="$2"
    local markers="$3"
    
    echo -e "${YELLOW}📋 Running $test_name tests...${NC}"
    
    local cmd="python -m pytest $test_path $VERBOSE $COVERAGE"
    
    if [[ -n "$markers" ]]; then
        cmd="$cmd -m $markers"
    fi
    
    if [[ "$COVERAGE" == "--cov" ]]; then
        cmd="$cmd --cov-report=html:$REPORTS_DIR/coverage-$test_name"
        cmd="$cmd --cov-report=term-missing"
    fi
    
    cmd="$cmd --html=$REPORTS_DIR/report-$test_name.html --self-contained-html"
    
    echo "Command: $cmd"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $test_name tests passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name tests failed${NC}"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
    
    # Check Python
    if ! command_exists python; then
        echo -e "${RED}❌ Python not found${NC}"
        exit 1
    fi
    
    # Check pip
    if ! command_exists pip; then
        echo -e "${RED}❌ pip not found${NC}"
        exit 1
    fi
    
    # Check if test requirements are installed
    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
        pip install -r "$TEST_DIR/test-requirements.txt"
    fi
    
    echo -e "${GREEN}✅ Dependencies ready${NC}"
}

# Function to setup test environment
setup_test_environment() {
    echo -e "${YELLOW}🔧 Setting up test environment...${NC}"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT:$BACKEND_DIR:$PYTHONPATH"
    export TEST_API_URL="http://localhost:8000"
    export TEST_FRONTEND_URL="http://localhost:5173"
    
    # Create necessary directories
    mkdir -p "$REPORTS_DIR"
    
    echo -e "${GREEN}✅ Environment ready${NC}"
}

# Function to start backend server for testing
start_backend() {
    echo -e "${YELLOW}🚀 Starting backend server...${NC}"
    
    cd "$BACKEND_DIR"
    
    # Check if server is already running
    if curl -s "http://localhost:8000/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend server already running${NC}"
        return 0
    fi
    
    # Start backend server in background
    python main.py &
    BACKEND_PID=$!
    
    # Wait for server to start
    for i in {1..30}; do
        if curl -s "http://localhost:8000/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Failed to start backend server${NC}"
    return 1
}

# Function to stop backend server
stop_backend() {
    if [[ -n "$BACKEND_PID" ]]; then
        echo -e "${YELLOW}🛑 Stopping backend server...${NC}"
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✅ Backend server stopped${NC}"
    fi
}

# Function to run security tests
run_security_tests() {
    echo -e "${YELLOW}🔒 Running security tests...${NC}"
    
    # Run bandit for security issues
    if command_exists bandit; then
        echo "Running bandit security scan..."
        bandit -r "$BACKEND_DIR" -f json -o "$REPORTS_DIR/bandit-report.json" || true
        bandit -r "$BACKEND_DIR" || true
    fi
    
    # Run safety for vulnerability check
    if command_exists safety; then
        echo "Running safety vulnerability check..."
        safety check --json --output "$REPORTS_DIR/safety-report.json" || true
        safety check || true
    fi
    
    echo -e "${GREEN}✅ Security tests completed${NC}"
}

# Function to run code quality tests
run_quality_tests() {
    echo -e "${YELLOW}📝 Running code quality tests...${NC}"
    
    # Run flake8 for style checking
    if command_exists flake8; then
        echo "Running flake8 style check..."
        flake8 "$BACKEND_DIR" --output-file="$REPORTS_DIR/flake8-report.txt" || true
    fi
    
    # Run mypy for type checking
    if command_exists mypy; then
        echo "Running mypy type check..."
        mypy "$BACKEND_DIR" --html-report "$REPORTS_DIR/mypy-report" || true
    fi
    
    echo -e "${GREEN}✅ Code quality tests completed${NC}"
}

# Trap to ensure cleanup
trap 'stop_backend' EXIT

# Main execution
echo -e "${BLUE}Starting test execution...${NC}"

# Check dependencies and setup
check_dependencies
setup_test_environment

# Initialize test results
TOTAL_TESTS=0
FAILED_TESTS=0

# Run tests based on type
case "$TEST_TYPE" in
    "unit")
        echo -e "${BLUE}🧪 Running Unit Tests${NC}"
        start_backend
        if run_tests "$TEST_DIR/backend" "backend" "unit"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        ;;
        
    "integration")
        echo -e "${BLUE}🔗 Running Integration Tests${NC}"
        start_backend
        if run_tests "$TEST_DIR/integration" "integration" "integration"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        ;;
        
    "e2e")
        echo -e "${BLUE}🌐 Running E2E Tests${NC}"
        if run_tests "$TEST_DIR/e2e" "e2e" "e2e"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        ;;
        
    "deployment")
        echo -e "${BLUE}🚀 Running Deployment Tests${NC}"
        if run_tests "$TEST_DIR/deployment" "deployment" "deployment"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        ;;
        
    "security")
        run_security_tests
        run_quality_tests
        ;;
        
    "all"|*)
        echo -e "${BLUE}🧪 Running All Tests${NC}"
        
        # Start backend for tests that need it
        start_backend
        
        # Backend tests
        if run_tests "$TEST_DIR/backend" "backend" "unit"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        
        # Frontend tests
        if run_tests "$TEST_DIR/frontend" "frontend" "frontend"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        
        # Integration tests
        if run_tests "$TEST_DIR/integration" "integration" "integration"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        
        # E2E tests (optional, may require additional setup)
        if run_tests "$TEST_DIR/e2e" "e2e" "e2e"; then
            ((TOTAL_TESTS++))
        else
            ((TOTAL_TESTS++)); ((FAILED_TESTS++))
        fi
        
        # Deployment tests (if requested)
        if [[ "$DEPLOYMENT" == "true" ]]; then
            if run_tests "$TEST_DIR/deployment" "deployment" "deployment"; then
                ((TOTAL_TESTS++))
            else
                ((TOTAL_TESTS++)); ((FAILED_TESTS++))
            fi
        fi
        
        # Security and quality tests
        run_security_tests
        run_quality_tests
        ;;
esac

# Generate summary report
echo ""
echo -e "${BLUE}📊 Test Summary${NC}"
echo "================"
echo "Total test suites: $TOTAL_TESTS"
echo "Failed test suites: $FAILED_TESTS"
echo "Success rate: $(( (TOTAL_TESTS - FAILED_TESTS) * 100 / TOTAL_TESTS ))%"

if [[ -d "$REPORTS_DIR" ]]; then
    echo ""
    echo -e "${BLUE}📋 Reports generated in: $REPORTS_DIR${NC}"
    ls -la "$REPORTS_DIR"
fi

# Exit with appropriate code
if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
