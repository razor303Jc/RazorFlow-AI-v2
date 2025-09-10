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
