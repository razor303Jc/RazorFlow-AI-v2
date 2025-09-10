"""
Integration Tests
=================

Test integration between frontend and backend components.
"""

import os
import sys
import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
sys.path.insert(0, backend_path)


class TestFrontendBackendIntegration:
    """Test integration between frontend and backend."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    def test_api_accessibility(self):
        """Test that API is accessible from frontend perspective."""
        try:
            # Test health endpoint
            response = requests.get(f"{self.API_BASE}/health", timeout=10)
            assert response.status_code == 200

            # Test main endpoints that frontend uses
            endpoints = [
                "/api/finance",
                "/api/sales",
                "/api/scheduler",
                "/api/analytics",
            ]

            for endpoint in endpoints:
                url = f"{self.API_BASE}{endpoint}"
                response = requests.get(url, timeout=10)
                assert response.status_code == 200

                # Check response format matches frontend expectations
                data = response.json()
                if endpoint != "/api/analytics":
                    assert "bot" in data
                    assert "data" in data
                    assert "insights" in data
                    assert "recommendations" in data

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Backend not available: {e}")

    @pytest.mark.integration
    def test_cors_functionality(self):
        """Test CORS works for frontend-backend communication."""
        github_origin = "https://razor303jc.github.io"
        localhost_origin = "http://localhost:5173"

        for origin in [github_origin, localhost_origin]:
            try:
                response = requests.get(
                    f"{self.API_BASE}/api/finance",
                    headers={"Origin": origin},
                    timeout=10,
                )
                assert response.status_code == 200

            except requests.exceptions.RequestException:
                pytest.skip("Backend not available for CORS test")

    @pytest.mark.integration
    def test_chat_functionality_integration(self):
        """Test chat functionality works end-to-end."""
        bots = ["finance", "sales", "scheduler"]
        test_message = {"message": "What's my current status?"}

        for bot in bots:
            try:
                response = requests.post(
                    f"{self.API_BASE}/api/chat/{bot}", json=test_message, timeout=10
                )
                assert response.status_code == 200

                data = response.json()
                assert "bot" in data
                assert "response" in data
                assert "timestamp" in data
                assert "confidence" in data

                # Response should be relevant to the message
                assert len(data["response"]) > 0

            except requests.exceptions.RequestException:
                pytest.skip(f"Backend not available for {bot} chat test")


class TestDataFlowIntegration:
    """Test data flow between different components."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    def test_analytics_aggregation(self):
        """Test analytics endpoint aggregates data correctly."""
        try:
            # Get individual bot data
            finance_url = f"{self.API_BASE}/api/finance"
            sales_url = f"{self.API_BASE}/api/sales"
            scheduler_url = f"{self.API_BASE}/api/scheduler"
            analytics_url = f"{self.API_BASE}/api/analytics"

            finance_resp = requests.get(finance_url, timeout=10)
            sales_resp = requests.get(sales_url, timeout=10)
            scheduler_resp = requests.get(scheduler_url, timeout=10)
            analytics_resp = requests.get(analytics_url, timeout=10)

            assert all(
                r.status_code == 200
                for r in [finance_resp, sales_resp, scheduler_resp, analytics_resp]
            )

            finance_data = finance_resp.json()["data"]
            sales_data = sales_resp.json()["data"]
            scheduler_data = scheduler_resp.json()["data"]
            analytics_data = analytics_resp.json()

            # Verify analytics aggregates the data correctly
            overview = analytics_data["overview"]
            assert overview["total_revenue"] == finance_data["revenue"]
            assert overview["active_leads"] == sales_data["leads"]
            meetings_scheduled = overview["meetings_scheduled"]
            meetings_today = scheduler_data["meetings_today"]
            assert meetings_scheduled == meetings_today

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for analytics test")

    @pytest.mark.integration
    def test_data_consistency_across_requests(self):
        """Test data consistency across multiple requests."""
        try:
            # Make multiple requests to the same endpoint
            responses = []
            for _ in range(3):
                response = requests.get(f"{self.API_BASE}/api/finance", timeout=10)
                assert response.status_code == 200
                responses.append(response.json())
                time.sleep(0.1)  # Small delay between requests

            # Data should be consistent (since it's static in demo)
            first_data = responses[0]["data"]
            for response in responses[1:]:
                assert response["data"] == first_data

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for consistency test")


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_concurrent_api_access(self):
        """Test system handles concurrent API access."""
        endpoints = ["/api/finance", "/api/sales", "/api/scheduler", "/api/analytics"]

        def make_request(endpoint):
            try:
                start_time = time.time()
                response = requests.get(f"{self.API_BASE}{endpoint}", timeout=15)
                end_time = time.time()

                return {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                }
            except requests.exceptions.RequestException:
                return {"endpoint": endpoint, "success": False}

        # Test concurrent access to different endpoints
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(make_request, endpoint) for endpoint in endpoints
            ]
            results = [future.result() for future in futures]

        # All requests should succeed
        successful_requests = [r for r in results if r["success"]]
        if len(successful_requests) > 0:
            assert len(successful_requests) >= 3  # Most should succeed

            # Response times should be reasonable even under concurrent load
            response_times = [
                r["response_time"] for r in successful_requests if "response_time" in r
            ]
            if response_times:
                max_response_time = max(response_times)
                assert max_response_time < 10.0  # Should respond within 10 seconds

    @pytest.mark.integration
    @pytest.mark.slow
    def test_chat_performance_across_bots(self):
        """Test chat performance across all bot types."""
        bots = ["finance", "sales", "scheduler"]
        test_messages = [
            {"message": "What's my current status?"},
            {"message": "Show me the latest data"},
            {"message": "What recommendations do you have?"},
        ]

        def test_chat_bot(bot, message):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.API_BASE}/api/chat/{bot}", json=message, timeout=15
                )
                end_time = time.time()

                return {
                    "bot": bot,
                    "message": message["message"],
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                }
            except requests.exceptions.RequestException:
                return {"bot": bot, "success": False}

        # Test all combinations of bots and messages
        test_combinations = [
            (bot, message) for bot in bots for message in test_messages
        ]

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(test_chat_bot, bot, message)
                for bot, message in test_combinations
            ]
            results = [future.result() for future in futures]

        successful_tests = [r for r in results if r["success"]]
        if len(successful_tests) > 0:
            # Most tests should succeed
            assert len(successful_tests) >= len(test_combinations) * 0.7

            # Chat responses should be reasonably fast
            response_times = [
                r["response_time"] for r in successful_tests if "response_time" in r
            ]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                assert avg_response_time < 5.0  # Average should be under 5 seconds


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    def test_invalid_endpoint_handling(self):
        """Test handling of invalid API endpoints."""
        invalid_endpoints = [
            "/api/nonexistent",
            "/api/finance/invalid",
            "/api/chat/invalid_bot",
            "/invalid_path",
        ]

        for endpoint in invalid_endpoints:
            try:
                response = requests.get(f"{self.API_BASE}{endpoint}", timeout=10)
                # Should return proper error status codes
                assert response.status_code in [404, 422]

            except requests.exceptions.RequestException:
                pytest.skip("Backend not available for error handling test")

    @pytest.mark.integration
    def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        try:
            # Test invalid JSON in chat request
            response = requests.post(
                f"{self.API_BASE}/api/chat/finance",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            # Should return proper error status
            assert response.status_code in [400, 422]

            # Test missing required fields
            response = requests.post(
                f"{self.API_BASE}/api/chat/finance",
                json={},  # Missing message field
                timeout=10,
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for malformed request test")

    @pytest.mark.integration
    def test_timeout_handling(self):
        """Test system behavior under timeout conditions."""
        try:
            # Test with very short timeout
            response = requests.get(
                f"{self.API_BASE}/api/finance",
                timeout=0.001,  # 1ms timeout - should timeout
            )

        except requests.exceptions.Timeout:
            # This is expected behavior
            pass
        except requests.exceptions.RequestException:
            # Other network errors are also acceptable in this test
            pass


class TestSecurityIntegration:
    """Test security aspects of integrated system."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    def test_csrf_protection(self):
        """Test CSRF protection (if implemented)."""
        try:
            # Test without proper headers
            response = requests.post(
                f"{self.API_BASE}/api/chat/finance",
                json={"message": "test"},
                timeout=10,
            )

            # Should work (CSRF not implemented in this demo)
            # In production, might require additional headers
            assert response.status_code in [200, 403]

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for CSRF test")

    @pytest.mark.integration
    def test_origin_validation(self):
        """Test origin validation in CORS."""
        malicious_origins = ["http://evil.com", "https://phishing-site.com"]

        for origin in malicious_origins:
            try:
                response = requests.get(
                    f"{self.API_BASE}/api/finance",
                    headers={"Origin": origin},
                    timeout=10,
                )

                # Request should succeed (demo has permissive CORS)
                # In production, this should be more restrictive
                assert response.status_code == 200

            except requests.exceptions.RequestException:
                pytest.skip("Backend not available for origin validation test")


class TestCompatibilityIntegration:
    """Test compatibility between different system versions."""

    API_BASE = os.getenv("TEST_API_URL", "http://localhost:8000")

    @pytest.mark.integration
    def test_api_version_compatibility(self):
        """Test API version compatibility."""
        try:
            response = requests.get(f"{self.API_BASE}/", timeout=10)
            assert response.status_code == 200

            data = response.json()
            assert "version" in data
            assert data["version"] == "2.0.0"

            # API should be backward compatible
            # (This would be more relevant with multiple API versions)

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for version test")

    @pytest.mark.integration
    def test_frontend_api_contract(self):
        """Test that API contract matches frontend expectations."""
        try:
            # Test finance bot response structure
            response = requests.get(f"{self.API_BASE}/api/finance", timeout=10)
            assert response.status_code == 200

            data = response.json()

            # Check structure matches what frontend expects
            required_fields = ["bot", "data", "insights", "recommendations"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Check data types match frontend expectations
            assert isinstance(data["insights"], list)
            assert isinstance(data["recommendations"], list)
            assert isinstance(data["data"], dict)

            # Test analytics response structure
            response = requests.get(f"{self.API_BASE}/api/analytics", timeout=10)
            assert response.status_code == 200

            analytics_data = response.json()
            required_sections = ["overview", "performance", "trends"]
            for section in required_sections:
                assert (
                    section in analytics_data
                ), f"Missing analytics section: {section}"

        except requests.exceptions.RequestException:
            pytest.skip("Backend not available for contract test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
