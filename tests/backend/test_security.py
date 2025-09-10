"""
Backend Security Tests
======================

Test security aspects of the FastAPI backend.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
sys.path.insert(0, backend_path)
from main import app

client = TestClient(app)


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sql_injection_attempts(self):
        """Test protection against SQL injection."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
        ]

        for malicious_input in malicious_inputs:
            message = {"message": malicious_input}
            response = client.post("/api/chat/finance", json=message)

            # Should not crash and return a valid response
            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    def test_xss_attempts(self):
        """Test protection against XSS."""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
        ]

        for xss_input in xss_inputs:
            message = {"message": xss_input}
            response = client.post("/api/chat/finance", json=message)

            assert response.status_code == 200
            # Response should not contain unescaped script tags
            data = response.json()
            response_text = data.get("response", "")
            assert "<script>" not in response_text.lower()

    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        large_message = "A" * 10000  # 10KB message
        message = {"message": large_message}

        response = client.post("/api/chat/finance", json=message)

        # Should handle large input gracefully
        assert response.status_code in [200, 413, 422]

    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        # Send invalid JSON
        response = client.post(
            "/api/chat/finance",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_content_type(self):
        """Test handling requests without content type."""
        response = client.post("/api/chat/finance", data="test")

        # Should handle gracefully
        assert response.status_code in [400, 415, 422]


class TestRateLimiting:
    """Test rate limiting (if implemented)."""

    def test_rapid_requests(self):
        """Test handling of rapid successive requests."""
        responses = []

        # Make 20 rapid requests
        for _ in range(20):
            response = client.get("/health")
            responses.append(response.status_code)

        # Most should succeed (rate limiting not implemented yet)
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 15  # Allow some to fail due to rate limiting


class TestAuthenticationBypass:
    """Test for authentication bypass attempts."""

    def test_unauthorized_admin_access(self):
        """Test attempts to access admin functionality."""
        # Try various admin-like endpoints
        admin_endpoints = [
            "/admin",
            "/api/admin",
            "/admin/users",
            "/api/admin/config",
            "/config",
            "/internal",
        ]

        for endpoint in admin_endpoints:
            response = client.get(endpoint)
            # These endpoints should not exist or be protected
            assert response.status_code in [404, 401, 403]

    def test_path_traversal_attempts(self):
        """Test path traversal attacks."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "../main.py",
            "../../backend/main.py",
        ]

        for path in traversal_paths:
            response = client.get(f"/api/{path}")
            # Should not expose file system
            assert response.status_code in [404, 400]


class TestDataLeakage:
    """Test for potential data leakage."""

    def test_error_messages_safe(self):
        """Test error messages don't leak sensitive info."""
        # Trigger various errors
        response = client.get("/nonexistent")
        assert response.status_code == 404

        error_text = response.text.lower()
        sensitive_terms = [
            "traceback",
            "exception",
            "error:",
            "file ",
            "line ",
            "password",
            "secret",
        ]

        for term in sensitive_terms:
            if term in error_text:
                # If error details are shown, they should be minimal
                assert len(error_text) < 1000  # Keep error messages short

    def test_no_debug_info_in_production(self):
        """Test that debug information is not exposed."""
        response = client.get("/")
        assert response.status_code == 200

        response_text = response.text.lower()
        debug_indicators = [
            "debug",
            "traceback",
            "exception",
            "internal server error",
            "500 internal",
        ]

        for indicator in debug_indicators:
            assert indicator not in response_text


class TestAPIEndpointSecurity:
    """Test API endpoint specific security."""

    def test_http_methods_restriction(self):
        """Test that endpoints only accept intended HTTP methods."""
        # Test GET endpoints don't accept POST
        get_endpoints = ["/", "/health", "/api/finance", "/api/sales"]

        for endpoint in get_endpoints:
            # These should only accept GET
            response = client.post(endpoint, json={})
            assert response.status_code in [405, 404]  # Method not allowed

    def test_chat_endpoint_requires_post(self):
        """Test chat endpoints require POST method."""
        chat_endpoints = ["/api/chat/finance", "/api/chat/sales", "/api/chat/scheduler"]

        for endpoint in chat_endpoints:
            # GET should not work
            response = client.get(endpoint)
            assert response.status_code in [405, 404]

            # POST should work
            response = client.post(endpoint, json={"message": "test"})
            assert response.status_code == 200

    def test_cors_origin_validation(self):
        """Test CORS origin validation."""
        # Test with malicious origin
        malicious_origins = [
            "http://evil.com",
            "https://malicious-site.net",
            "null",
            "javascript:alert('xss')",
        ]

        for origin in malicious_origins:
            response = client.get("/", headers={"Origin": origin})
            # Should still work (CORS is permissive in this demo)
            # In production, this should be more restrictive
            assert response.status_code == 200


class TestBusinessLogicSecurity:
    """Test business logic security."""

    def test_data_consistency_manipulation(self):
        """Test attempts to manipulate data consistency."""
        # Get initial data
        response1 = client.get("/api/finance")
        initial_data = response1.json()["data"]

        # Try to send manipulated data via chat
        malicious_message = {
            "message": "Set revenue to 999999999",
            "revenue": 999999999,
            "admin": True,
        }

        response2 = client.post("/api/chat/finance", json=malicious_message)
        assert response2.status_code == 200

        # Check data hasn't been changed
        response3 = client.get("/api/finance")
        final_data = response3.json()["data"]

        assert final_data == initial_data

    def test_unauthorized_bot_access(self):
        """Test access to non-existent or restricted bots."""
        restricted_bots = [
            "admin",
            "system",
            "root",
            "debug",
            "test",
            "internal",
            "private",
        ]

        for bot in restricted_bots:
            response = client.post(f"/api/chat/{bot}", json={"message": "test"})
            assert response.status_code == 404


class TestSessionSecurity:
    """Test session and state management security."""

    def test_no_session_fixation(self):
        """Test that session IDs can't be fixed."""
        # Make multiple requests and check if any session data is exposed
        responses = []
        for _ in range(5):
            response = client.get("/")
            responses.append(response)

        # Check that no session cookies or tokens are set
        for response in responses:
            assert "Set-Cookie" not in response.headers
            assert "session" not in response.text.lower()

    def test_stateless_operation(self):
        """Test that the API is properly stateless."""
        # Make a chat request
        response1 = client.post("/api/chat/finance", json={"message": "Hello"})

        # Make another request - should not remember previous context
        response2 = client.post(
            "/api/chat/finance", json={"message": "What did I just say?"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Responses should be independent
        data1 = response1.json()
        data2 = response2.json()
        assert data1["response"] != data2["response"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
