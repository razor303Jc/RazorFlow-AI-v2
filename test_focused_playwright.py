"""
Focused Playwright test for frontend testing outside container
"""

from playwright.sync_api import sync_playwright
import time


def test_api_endpoints():
    """Test API endpoints work correctly."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        print("🧪 Testing RazorFlow AI API Endpoints")
        print("=" * 40)

        # Test backend health
        print("🔍 Testing backend health...")
        response = page.request.get("http://localhost:8000/health")
        assert response.status == 200
        health_data = response.json()
        print(f"✅ Health: {health_data['status']}")

        # Test Finance API
        print("🔍 Testing Finance API...")
        response = page.request.get("http://localhost:8000/api/finance")
        assert response.status == 200
        finance_data = response.json()
        assert finance_data["bot"] == "Finance AI"
        print(f"✅ Finance API: {finance_data['data']['revenue']} revenue")

        # Test Sales API
        print("🔍 Testing Sales API...")
        response = page.request.get("http://localhost:8000/api/sales")
        assert response.status == 200
        sales_data = response.json()
        assert sales_data["bot"] == "Sales AI"
        print(f"✅ Sales API: {sales_data['data']['leads']} leads")

        # Test Scheduler API
        print("🔍 Testing Scheduler API...")
        response = page.request.get("http://localhost:8000/api/scheduler")
        assert response.status == 200
        scheduler_data = response.json()
        assert scheduler_data["bot"] == "Scheduler AI"
        print(f"✅ Scheduler API: {scheduler_data['data']['meetings_today']} meetings")

        print("\n🎉 All API tests passed!")

        browser.close()


def test_frontend_navigation():
    """Test frontend navigation and interaction."""

    with sync_playwright() as p:
        # Launch browser in non-headless mode for visual testing
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        print("\n🌐 Testing Frontend Navigation")
        print("=" * 40)

        # Try to access frontend
        frontend_urls = [
            "http://localhost:5174",
            "http://localhost:5173",
            "http://localhost:5174/RazorFlow-AI-v2/",
            "http://localhost:5173/RazorFlow-AI-v2/",
        ]

        frontend_loaded = False
        working_url = None

        for url in frontend_urls:
            try:
                print(f"🔍 Trying {url}...")
                page.goto(url, timeout=5000, wait_until="domcontentloaded")

                # Check if page loaded successfully (not 404)
                if "404" not in page.content() and page.title():
                    frontend_loaded = True
                    working_url = url
                    print(f"✅ Frontend loaded at {url}")
                    print(f"   Page title: {page.title()}")
                    break

            except Exception as e:
                print(f"❌ Failed to load {url}: {str(e)[:50]}...")
                continue

        if frontend_loaded:
            print("\n🔍 Frontend is accessible for manual testing!")
            print(f"Working URL: {working_url}")

            # Keep browser open for manual testing
            print("\n⏰ Keeping browser open for 15 seconds for manual testing...")
            print("   You can interact with the frontend now!")
            time.sleep(15)
        else:
            print("\n⚠️  Frontend not accessible on tested ports")
            print("   Backend API is working though!")
            # Still keep browser open briefly
            time.sleep(5)

        browser.close()


if __name__ == "__main__":
    print("🚀 RazorFlow AI - Playwright Testing Outside Container")
    print("=" * 55)

    # Test API endpoints first
    test_api_endpoints()

    # Test frontend navigation
    test_frontend_navigation()

    print("\n🎯 Testing Complete!")
    print("Backend API is ready for frontend development and testing.")
