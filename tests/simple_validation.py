#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test Validation
Test basic functionality to verify framework setup
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_imports():
    """Test that all required imports work"""
    try:
        import pytest
        import fastapi
        import httpx
        from main import app

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_fastapi_app():
    """Test FastAPI app initialization"""
    try:
        from main import app

        assert app.title == "RazorFlow AI Backend"
        assert "2.0.0" in app.version
        print("✅ FastAPI app validation successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False


def test_pytest_discovery():
    """Test pytest can discover test files"""
    try:
        import subprocess

        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        if result.returncode == 0:
            print("✅ Pytest discovery successful")
            return True
        else:
            print(f"⚠️ Pytest discovery had issues: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Pytest discovery failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Running simple test validation...")

    tests = [test_imports, test_fastapi_app, test_pytest_discovery]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All validation tests passed! Framework is ready.")
        sys.exit(0)
    else:
        print("⚠️ Some validation tests failed. Check output above.")
        sys.exit(1)
