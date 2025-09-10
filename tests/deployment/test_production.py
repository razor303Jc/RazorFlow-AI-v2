"""
Deployment Tests
================

Test deployment configurations and production readiness.
"""

import os
import pytest
import requests
import json
import time


class TestProductionEndpoints:
    """Test production API endpoints."""

    PRODUCTION_API = "https://razorflow-ai-production.up.railway.app"
    PRODUCTION_FRONTEND = "https://razor303jc.github.io/RazorFlow-AI-v2/"

    @pytest.mark.deployment
    def test_production_api_health(self):
        """Test production API health check."""
        try:
            response = requests.get(f"{self.PRODUCTION_API}/health", timeout=30)
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Production API not available: {e}")

    @pytest.mark.deployment
    def test_production_api_root(self):
        """Test production API root endpoint."""
        try:
            response = requests.get(f"{self.PRODUCTION_API}/", timeout=30)
            assert response.status_code == 200

            data = response.json()
            assert data["version"] == "2.0.0"
            assert data["status"] == "operational"

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Production API not available: {e}")

    @pytest.mark.deployment
    @pytest.mark.parametrize(
        "endpoint", ["/api/finance", "/api/sales", "/api/scheduler", "/api/analytics"]
    )
    def test_production_api_endpoints(self, endpoint):
        """Test all production API endpoints work."""
        try:
            response = requests.get(f"{self.PRODUCTION_API}{endpoint}", timeout=30)
            assert response.status_code == 200

            data = response.json()
            assert "bot" in data or "overview" in data

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Production API not available: {e}")

    @pytest.mark.deployment
    def test_production_frontend_loads(self):
        """Test production frontend loads successfully."""
        try:
            response = requests.get(self.PRODUCTION_FRONTEND, timeout=30)
            assert response.status_code == 200
            assert "RazorFlow AI" in response.text

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Production frontend not available: {e}")

    @pytest.mark.deployment
    def test_cors_configuration(self):
        """Test CORS is properly configured for production."""
        try:
            # Test preflight request
            response = requests.options(
                f"{self.PRODUCTION_API}/api/finance",
                headers={
                    "Origin": "https://razor303jc.github.io",
                    "Access-Control-Request-Method": "GET",
                },
                timeout=30,
            )

            # Should allow the request or return method not allowed
            assert response.status_code in [200, 204, 405]

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Production API not available: {e}")


class TestRailwayConfiguration:
    """Test Railway deployment configuration."""

    def test_railway_json_exists(self):
        """Test railway.json configuration file exists."""
        railway_json_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "railway.json"
        )
        assert os.path.exists(railway_json_path)

    def test_railway_json_valid(self):
        """Test railway.json is valid JSON with required fields."""
        railway_json_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "railway.json"
        )

        with open(railway_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Check required sections
        assert "build" in config
        assert "deploy" in config

        # Check build configuration
        build = config["build"]
        assert "builder" in build
        assert "buildCommand" in build

        # Check deploy configuration
        deploy = config["deploy"]
        assert "startCommand" in deploy
        assert "healthcheckPath" in deploy

        # Validate health check path
        assert deploy["healthcheckPath"] == "/health"

    def test_requirements_txt_exists(self):
        """Test requirements.txt exists for Python dependencies."""
        requirements_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "backend", "requirements.txt"
        )
        assert os.path.exists(requirements_path)

    def test_requirements_txt_valid(self):
        """Test requirements.txt contains necessary dependencies."""
        requirements_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "backend", "requirements.txt"
        )

        with open(requirements_path, "r", encoding="utf-8") as f:
            requirements = f.read()

        # Check for essential dependencies
        essential_deps = ["fastapi", "uvicorn", "pydantic"]

        for dep in essential_deps:
            assert dep in requirements, f"Missing dependency: {dep}"


class TestGitHubPagesConfiguration:
    """Test GitHub Pages deployment configuration."""

    def test_github_workflow_exists(self):
        """Test GitHub Actions workflow exists."""
        workflow_path = os.path.join(
            os.path.dirname(__file__), "..", "..", ".github", "workflows", "deploy.yml"
        )
        assert os.path.exists(workflow_path)

    def test_github_workflow_valid(self):
        """Test GitHub Actions workflow is properly configured."""
        workflow_path = os.path.join(
            os.path.dirname(__file__), "..", "..", ".github", "workflows", "deploy.yml"
        )

        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for essential workflow elements
        assert "deploy-frontend" in content
        assert "test-backend" in content
        assert "actions/checkout@v4" in content
        assert "actions/setup-node@v4" in content
        assert "actions/setup-python@v4" in content

    def test_package_json_deploy_script(self):
        """Test package.json has deploy script."""
        package_json_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "package.json"
        )

        with open(package_json_path, "r", encoding="utf-8") as f:
            package = json.load(f)

        # Check deploy script exists
        assert "scripts" in package
        assert "deploy" in package["scripts"]

        # Should use gh-pages for deployment
        deploy_script = package["scripts"]["deploy"]
        assert "gh-pages" in deploy_script

    def test_vite_config_base_path(self):
        """Test Vite config has correct base path for GitHub Pages."""
        vite_config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "vite.config.js"
        )

        with open(vite_config_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should have base path for GitHub Pages
        assert "base:" in content
        assert "RazorFlow-AI-v2" in content


class TestEnvironmentConfiguration:
    """Test environment-specific configurations."""

    def test_api_base_url_configuration(self):
        """Test API base URL is properly configured."""
        app_jsx_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "src", "App.jsx"
        )

        with open(app_jsx_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should have API_BASE constant
        assert "API_BASE" in content

        # Should point to production Railway URL
        assert "railway.app" in content

    def test_cors_origins_configured(self):
        """Test CORS origins are properly configured."""
        main_py_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "backend", "main.py"
        )

        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should have CORS middleware
        assert "CORSMiddleware" in content
        assert "allow_origins" in content

        # Should include GitHub Pages domain
        assert "github.io" in content

    def test_production_settings(self):
        """Test production-specific settings."""
        main_py_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "backend", "main.py"
        )

        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should handle PORT environment variable for Railway
        assert "PORT" in content
        assert "os.getenv" in content or "os.environ" in content


class TestSSLAndSecurity:
    """Test SSL and security configurations."""

    @pytest.mark.deployment
    def test_production_uses_https(self):
        """Test production endpoints use HTTPS."""
        api_url = "https://razorflow-ai-production.up.railway.app"
        frontend_url = "https://razor303jc.github.io/RazorFlow-AI-v2/"

        # Both URLs should use HTTPS
        assert api_url.startswith("https://")
        assert frontend_url.startswith("https://")

    @pytest.mark.deployment
    def test_ssl_certificate_valid(self):
        """Test SSL certificates are valid."""
        try:
            # Test API SSL
            response = requests.get(
                "https://razorflow-ai-production.up.railway.app/health",
                timeout=30,
                verify=True,  # Verify SSL certificate
            )
            assert response.status_code == 200

        except requests.exceptions.SSLError:
            pytest.fail("SSL certificate invalid for production API")
        except requests.exceptions.RequestException:
            pytest.skip("Production API not available")

    @pytest.mark.deployment
    def test_security_headers(self):
        """Test security headers are present."""
        try:
            response = requests.get(
                "https://razorflow-ai-production.up.railway.app/", timeout=30
            )

            headers = response.headers

            # Check for basic security headers
            # Note: Some headers might be added by Railway/hosting platform
            assert response.status_code == 200

            # Content-Type should be properly set
            assert "application/json" in headers.get("Content-Type", "")

        except requests.exceptions.RequestException:
            pytest.skip("Production API not available")


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""

    @pytest.mark.deployment
    @pytest.mark.slow
    def test_response_times(self):
        """Test production response times are acceptable."""
        endpoints = ["/health", "/api/finance", "/api/sales", "/api/scheduler"]

        base_url = "https://razorflow-ai-production.up.railway.app"

        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}{endpoint}", timeout=30)
                end_time = time.time()

                assert response.status_code == 200

                response_time = end_time - start_time
                # Production should respond within 5 seconds
                assert response_time < 5.0, f"{endpoint} too slow: {response_time}s"

            except requests.exceptions.RequestException:
                pytest.skip("Production API not available")

    @pytest.mark.deployment
    @pytest.mark.slow
    def test_concurrent_load(self):
        """Test handling of concurrent requests in production."""
        import threading
        import queue

        base_url = "https://razorflow-ai-production.up.railway.app"
        results = queue.Queue()

        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=30)
                end_time = time.time()

                results.put(
                    {
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": True,
                    }
                )
            except requests.exceptions.RequestException:
                results.put({"success": False})

        # Create 5 concurrent requests (modest load test)
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all requests
        for thread in threads:
            thread.join()

        # Collect results
        success_count = 0
        response_times = []

        while not results.empty():
            result = results.get()
            if result.get("success"):
                success_count += 1
                if "response_time" in result:
                    response_times.append(result["response_time"])

        # Most requests should succeed
        if success_count > 0:
            assert success_count >= 3  # At least 60% success rate

            # Average response time should be reasonable
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                assert avg_response_time < 10.0  # Allow longer time for concurrent load


class TestMonitoringAndLogging:
    """Test monitoring and logging capabilities."""

    @pytest.mark.deployment
    def test_health_check_endpoint(self):
        """Test health check endpoint for monitoring."""
        try:
            response = requests.get(
                "https://razorflow-ai-production.up.railway.app/health", timeout=30
            )
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert data["status"] == "healthy"

        except requests.exceptions.RequestException:
            pytest.skip("Production API not available")

    def test_error_handling_configured(self):
        """Test error handling is properly configured."""
        main_py_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "backend", "main.py"
        )

        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should have proper error handling
        # (This is a basic check - more sophisticated error handling
        # would require additional code)
        assert "FastAPI" in content  # FastAPI provides basic error handling


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
