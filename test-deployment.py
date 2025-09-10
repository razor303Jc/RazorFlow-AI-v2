"""
Simple API health check test to verify local deployment.
Run this to test if the backend is working correctly.
"""

import requests
import time


def test_backend_health():
    """Test if backend server is responding."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False


def test_frontend_health():
    """Test if frontend server is responding."""
    # Try both possible frontend ports
    frontend_urls = ["http://localhost:5173", "http://localhost:5174"]

    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302]:  # 302 is redirect, which is fine
                print(f"✅ Frontend server is responding at {url}!")
                return True
        except requests.exceptions.RequestException:
            continue

    print("❌ Frontend server not responding on ports 5173 or 5174")
    return False


def test_api_docs():
    """Test if API documentation is accessible."""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation is accessible!")
            return True
        else:
            print(f"❌ API docs returned: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs connection failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing RazorFlow AI Local Deployment")
    print("=" * 40)

    # Wait a moment for servers to be ready
    print("⏳ Waiting for servers to be ready...")
    time.sleep(2)

    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    docs_ok = test_api_docs()

    print("\n📊 Test Results:")
    print("=" * 20)

    if backend_ok and frontend_ok and docs_ok:
        print("🎉 All tests passed! Your local deployment is working perfectly.")
        print("\n🔗 Access your application:")
        print("  • Frontend: http://localhost:5173")
        print("  • Backend API: http://localhost:8000")
        print("  • API Documentation: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the server logs.")

    print("\n🎭 Once Playwright installation completes, run:")
    print("  ./run-playwright.sh")
