"""
RazorFlow AI Test Framework Configuration
=========================================

This module contains configuration and fixtures for the entire test suite.
"""

import os
import sys
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
import subprocess
import time

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Test environment variables
TEST_CONFIG = {
    "API_BASE_URL": os.getenv("TEST_API_URL", "http://localhost:8000"),
    "FRONTEND_URL": os.getenv("TEST_FRONTEND_URL", "http://localhost:5173"),
    "PRODUCTION_API": "https://razorflow-ai-production.up.railway.app",
    "PRODUCTION_FRONTEND": "https://razor303jc.github.io/RazorFlow-AI-v2/",
    "TEST_TIMEOUT": int(os.getenv("TEST_TIMEOUT", "30")),
    "SLOW_TEST_THRESHOLD": int(os.getenv("SLOW_TEST_THRESHOLD", "5")),
}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def backend_server():
    """Start backend server for testing."""
    # Check if server is already running
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{TEST_CONFIG['API_BASE_URL']}/health")
            if response.status_code == 200:
                yield TEST_CONFIG["API_BASE_URL"]
                return
    except:
        pass

    # Start the server
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=os.path.join(os.path.dirname(__file__), "..", "backend"),
    )

    # Wait for server to start
    for _ in range(30):
        try:
            async with AsyncClient() as client:
                response = await client.get(f"{TEST_CONFIG['API_BASE_URL']}/health")
                if response.status_code == 200:
                    break
        except:
            pass
        await asyncio.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Backend server failed to start")

    yield TEST_CONFIG["API_BASE_URL"]

    process.terminate()
    process.wait()


@pytest.fixture
async def async_client(backend_server: str) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing."""
    async with AsyncClient(base_url=backend_server, timeout=30.0) as client:
        yield client


@pytest.fixture
def sync_client(backend_server: str):
    """Create sync HTTP client for simple requests."""
    import requests

    return requests.Session()


@pytest.fixture(scope="session")
def test_data():
    """Test data for various scenarios."""
    return {
        "valid_chat_message": {"message": "What is my current revenue?"},
        "invalid_chat_message": {"message": ""},
        "sample_finance_data": {
            "revenue": 125000,
            "expenses": 75000,
            "profit": 50000,
            "growth": 15.5,
        },
        "sample_sales_data": {
            "leads": 234,
            "conversions": 45,
            "pipeline_value": 500000,
            "close_rate": 19.2,
        },
    }


@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    os.unlink(tmp.name)


class PerformanceTracker:
    """Track performance metrics during tests."""

    def __init__(self):
        self.metrics = {}

    def record(self, test_name: str, duration: float, memory_usage: float = None):
        """Record performance metric."""
        self.metrics[test_name] = {
            "duration": duration,
            "memory_usage": memory_usage,
            "timestamp": time.time(),
        }

    def get_slow_tests(self, threshold: float = 5.0):
        """Get tests that exceeded threshold."""
        return {
            name: data
            for name, data in self.metrics.items()
            if data["duration"] > threshold
        }


@pytest.fixture(scope="session")
def performance_tracker():
    """Global performance tracker."""
    return PerformanceTracker()


# Custom markers for test categorization
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Configure test markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "deployment: Deployment tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "frontend: Frontend tests")
    config.addinivalue_line("markers", "backend: Backend tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "performance: Performance tests")


def pytest_runtest_setup(item):
    """Setup before each test."""
    # Mark slow tests
    if hasattr(item, "callspec") and "slow" in str(item.callspec):
        pytest.mark.slow(item)


def pytest_runtest_teardown(item):
    """Cleanup after each test."""
    # Clean up any test artifacts
    pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add backend marker to backend tests
        if "backend" in str(item.fspath):
            item.add_marker(pytest.mark.backend)

        # Add frontend marker to frontend tests
        if "frontend" in str(item.fspath):
            item.add_marker(pytest.mark.frontend)

        # Add deployment marker to deployment tests
        if "deployment" in str(item.fspath):
            item.add_marker(pytest.mark.deployment)

        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to e2e tests
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
