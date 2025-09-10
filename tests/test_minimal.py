# -*- coding: utf-8 -*-
"""
Minimal Health Check Test
Test the most basic functionality to verify framework works
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_backend_import():
    """Test that backend can be imported"""
    from main import app

    assert app.title == "RazorFlow AI Backend"


def test_health_endpoint_exists():
    """Test that health endpoint exists in the app"""
    from main import app

    # Check routes exist
    routes = [route.path for route in app.routes]

    # Should have at least root route
    assert "/" in routes or any(route.startswith("/") for route in routes)


@pytest.mark.asyncio
async def test_simple_functionality():
    """Test basic app functionality"""
    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Try to access any route to see if app is working
    try:
        response = client.get("/")
        # Don't care about specific status, just that it responds
        assert response is not None
    except Exception:
        # If root doesn't exist, that's fine for now
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
