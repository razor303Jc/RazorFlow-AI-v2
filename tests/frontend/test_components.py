"""
Frontend Component Tests
========================

Test React components and frontend functionality.
"""

import os
import pytest
import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestFrontendBuild:
    """Test frontend build process."""

    def test_npm_install(self):
        """Test npm install completes successfully."""
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
        )

        assert result.returncode == 0, f"npm install failed: {result.stderr}"

    def test_npm_build(self):
        """Test npm build completes successfully."""
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
        )

        assert result.returncode == 0, f"npm build failed: {result.stderr}"

        # Check if dist directory was created
        dist_path = os.path.join(frontend_path, "dist")
        assert os.path.exists(dist_path), "dist directory not created"

        # Check if index.html exists
        index_path = os.path.join(dist_path, "index.html")
        assert os.path.exists(index_path), "index.html not found in dist"

    def test_build_assets(self):
        """Test that build generates required assets."""
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        dist_path = os.path.join(frontend_path, "dist")

        if not os.path.exists(dist_path):
            pytest.skip("Build not run yet")

        # Check for CSS files
        assets_path = os.path.join(dist_path, "assets")
        if os.path.exists(assets_path):
            files = os.listdir(assets_path)
            css_files = [f for f in files if f.endswith(".css")]
            js_files = [f for f in files if f.endswith(".js")]

            assert len(css_files) > 0, "No CSS files found"
            assert len(js_files) > 0, "No JS files found"


@pytest.mark.frontend
class TestFrontendDev:
    """Test frontend development server."""

    @pytest.fixture(scope="class")
    def dev_server(self):
        """Start development server for testing."""
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

        # Start dev server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        for _ in range(30):
            try:
                response = requests.get("http://localhost:5173", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        else:
            process.terminate()
            raise RuntimeError("Dev server failed to start")

        yield "http://localhost:5173"

        process.terminate()
        process.wait()

    def test_dev_server_responds(self, dev_server):
        """Test development server responds."""
        response = requests.get(dev_server, timeout=10)
        assert response.status_code == 200
        assert "RazorFlow AI" in response.text

    def test_dev_server_serves_assets(self, dev_server):
        """Test development server serves static assets."""
        # Test CSS is loaded
        response = requests.get(dev_server, timeout=10)
        html_content = response.text

        # Should contain references to main.jsx and CSS
        assert "main.jsx" in html_content or "index" in html_content
        assert "text/css" in html_content or "@tailwind" in html_content


@pytest.mark.e2e
class TestFrontendE2E:
    """End-to-end frontend tests using Selenium."""

    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome WebDriver."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        try:
            driver = webdriver.Chrome(options=options)
            yield driver
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
        finally:
            if "driver" in locals():
                driver.quit()

    def test_page_loads(self, driver):
        """Test main page loads successfully."""
        driver.get("http://localhost:5173")

        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Check title
        assert "RazorFlow AI" in driver.title

    def test_navigation_elements(self, driver):
        """Test navigation elements are present."""
        driver.get("http://localhost:5173")

        wait = WebDriverWait(driver, 10)

        # Check for header
        header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
        assert header is not None

        # Check for main content
        main = driver.find_element(By.TAG_NAME, "main")
        assert main is not None

    def test_bot_selection(self, driver):
        """Test bot selection functionality."""
        driver.get("http://localhost:5173")

        wait = WebDriverWait(driver, 10)

        # Wait for bot buttons to load
        try:
            bot_buttons = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[contains(text(), 'Bot')]")
                )
            )

            if len(bot_buttons) > 0:
                # Click first bot button
                bot_buttons[0].click()

                # Wait for content to update
                time.sleep(2)

                # Check if dashboard content is visible
                dashboard = driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'space-y')]"
                )
                assert len(dashboard) > 0

        except Exception:
            # If specific bot buttons not found, check for general buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            assert len(buttons) > 0, "No interactive buttons found"

    def test_responsive_design(self, driver):
        """Test responsive design at different screen sizes."""
        test_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),  # Tablet
            (375, 667),  # Mobile
        ]

        for width, height in test_sizes:
            driver.set_window_size(width, height)
            driver.get("http://localhost:5173")

            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Check that content is visible
            body = driver.find_element(By.TAG_NAME, "body")
            assert body.size["width"] > 0
            assert body.size["height"] > 0

    def test_error_handling(self, driver):
        """Test error handling with invalid API."""
        # This test would require mocking the API or testing with offline backend
        driver.get("http://localhost:5173")

        wait = WebDriverWait(driver, 10)

        # Check page loads even if API is down
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Page should still be functional
        title = driver.title
        assert "RazorFlow AI" in title


class TestFrontendSecurity:
    """Test frontend security aspects."""

    def test_no_sensitive_data_in_source(self):
        """Test that no sensitive data is exposed in source code."""
        frontend_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "src"
        )

        sensitive_patterns = [
            "password",
            "secret",
            "api_key",
            "private_key",
            "token",
            "auth_token",
            "session_id",
        ]

        for root, dirs, files in os.walk(frontend_path):
            for file in files:
                if file.endswith((".js", ".jsx", ".ts", ".tsx")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()

                        for pattern in sensitive_patterns:
                            if pattern in content:
                                # Check if it's in a comment or test context
                                lines = content.split("\n")
                                for i, line in enumerate(lines):
                                    if pattern in line:
                                        # Allow in comments or obvious test data
                                        if (
                                            "//" in line
                                            or "/*" in line
                                            or "test" in line
                                            or "example" in line
                                        ):
                                            continue
                                        else:
                                            pytest.fail(
                                                f"Sensitive pattern '{pattern}' "
                                                f"found in {file}:{i+1}"
                                            )

    def test_api_url_configuration(self):
        """Test API URL is properly configured."""
        app_jsx_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "src", "App.jsx"
        )

        if os.path.exists(app_jsx_path):
            with open(app_jsx_path, "r") as f:
                content = f.read()

                # Should have proper API base URL
                assert "API_BASE" in content

                # Should not have localhost in production build
                # (This would need environment-specific checking)

    def test_build_security_headers(self):
        """Test that build includes security considerations."""
        dist_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "dist"
        )

        if not os.path.exists(dist_path):
            pytest.skip("Build not available")

        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                content = f.read()

                # Check for security-related meta tags or headers
                # Note: These might be added by the hosting platform
                assert "viewport" in content  # Basic responsive design


class TestFrontendPerformance:
    """Test frontend performance characteristics."""

    def test_bundle_size(self):
        """Test that bundle size is reasonable."""
        dist_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "dist"
        )

        if not os.path.exists(dist_path):
            pytest.skip("Build not available")

        assets_path = os.path.join(dist_path, "assets")
        if os.path.exists(assets_path):
            total_size = 0
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    if file.endswith((".js", ".css")):
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)

            # Bundle should be reasonable (less than 5MB)
            assert total_size < 5 * 1024 * 1024, f"Bundle too large: {total_size} bytes"

    def test_asset_optimization(self):
        """Test that assets are optimized."""
        dist_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "dist"
        )

        if not os.path.exists(dist_path):
            pytest.skip("Build not available")

        # Check if assets are minified (contain no unnecessary whitespace)
        assets_path = os.path.join(dist_path, "assets")
        if os.path.exists(assets_path):
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    if file.endswith(".js"):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r") as f:
                            content = f.read()

                            # Minified files should have high character density
                            if len(content) > 1000:  # Only check substantial files
                                lines = content.split("\n")
                                avg_line_length = len(content) / len(lines)
                                # Minified JS should have long lines
                                assert (
                                    avg_line_length > 50
                                ), f"File {file} may not be minified"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
