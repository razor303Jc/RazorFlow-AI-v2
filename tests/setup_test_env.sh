#!/bin/bash

echo "🧪 Setting up RazorFlow AI Test Environment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")/.." || exit

# Create test environment if it doesn't exist
if [ ! -d "test-env" ]; then
    echo -e "${YELLOW}📦 Creating test virtual environment...${NC}"
    python3 -m venv test-env
fi

# Activate test environment
echo -e "${YELLOW}🔄 Activating test environment...${NC}"
source test-env/bin/activate

# Install test dependencies
echo -e "${YELLOW}📥 Installing test dependencies...${NC}"
pip install --upgrade pip

# Install core testing dependencies
pip install pytest pytest-asyncio pytest-html pytest-cov

# Install Playwright and its dependencies
echo -e "${YELLOW}🎭 Installing Playwright...${NC}"
pip install playwright pytest-playwright

# Install Playwright browsers
echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
playwright install

# Install additional test dependencies
pip install requests httpx faker

# Install backend dependencies for testing
echo -e "${YELLOW}📦 Installing backend dependencies for testing...${NC}"
pip install -r backend/requirements.txt

# Create test configuration
echo -e "${YELLOW}🔧 Creating test configuration...${NC}"
cat > tests/pytest.ini << EOF
[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --html=test-results/report.html
    --self-contained-html
    --cov=../backend
    --cov-report=html:test-results/coverage
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    playwright: Playwright browser tests
    slow: Tests that take a long time
    skip_ci: Tests to skip in CI
    database: Tests that require database
    api: API tests
    frontend: Frontend tests
    backend: Backend tests
asyncio_mode = auto
EOF

# Create playwright configuration
echo -e "${YELLOW}🎭 Creating Playwright configuration...${NC}"
cat > tests/playwright.config.py << 'EOF'
"""Playwright configuration for RazorFlow AI tests."""

from playwright.sync_api import Playwright
import os

# Test configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Browser configuration
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))

# Timeout configuration
TIMEOUT = int(os.getenv("TIMEOUT", "30000"))
NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))

# Screenshot and video configuration
SCREENSHOT_MODE = os.getenv("SCREENSHOT_MODE", "on-failure")
VIDEO_MODE = os.getenv("VIDEO_MODE", "on-failure")

# Test data configuration
TEST_USER_EMAIL = "test@razorflow.ai"
TEST_USER_PASSWORD = "testpassword123"

def get_browser_config():
    """Get browser configuration for Playwright tests."""
    return {
        "headless": HEADLESS,
        "slow_mo": SLOW_MO,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
        ]
    }

def get_context_config():
    """Get context configuration for Playwright tests."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "record_video_dir": "test-results/videos" if VIDEO_MODE != "off" else None,
        "record_video_size": {"width": 1280, "height": 720},
    }

def get_page_config():
    """Get page configuration for Playwright tests."""
    return {
        "default_timeout": TIMEOUT,
        "default_navigation_timeout": NAVIGATION_TIMEOUT,
    }
EOF

# Create test results directory
mkdir -p test-results/screenshots
mkdir -p test-results/videos

echo -e "\n${GREEN}🎉 Test environment setup complete!${NC}"
echo -e "${BLUE}Test Environment Info:${NC}"
echo -e "  • Python: ${YELLOW}$(python --version)${NC}"
echo -e "  • Pytest: ${YELLOW}$(pytest --version | head -n1)${NC}"
echo -e "  • Playwright: ${YELLOW}$(python -c "import playwright; print(f'Playwright {playwright.__version__}')")${NC}"

echo -e "\n${BLUE}Available Commands:${NC}"
echo -e "  • Run all tests: ${YELLOW}pytest${NC}"
echo -e "  • Run unit tests: ${YELLOW}pytest -m unit${NC}"
echo -e "  • Run integration tests: ${YELLOW}pytest -m integration${NC}"
echo -e "  • Run Playwright tests: ${YELLOW}pytest -m playwright${NC}"
echo -e "  • Run with coverage: ${YELLOW}pytest --cov${NC}"

echo -e "\n${BLUE}Test Reports Location:${NC}"
echo -e "  • HTML Report: ${YELLOW}test-results/report.html${NC}"
echo -e "  • Coverage Report: ${YELLOW}test-results/coverage/index.html${NC}"
echo -e "  • Screenshots: ${YELLOW}test-results/screenshots/${NC}"
echo -e "  • Videos: ${YELLOW}test-results/videos/${NC}"
