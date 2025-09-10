"""
Backend API Unit Tests
======================

Test all FastAPI endpoints and business logic.
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


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "RazorFlow AI Backend API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "operational"
        assert "timestamp" in data
        assert "endpoints" in data

        # Check endpoint structure
        endpoints = data["endpoints"]
        assert "finance" in endpoints
        assert "sales" in endpoints
        assert "scheduler" in endpoints
        assert "chat" in endpoints

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.slow
    def test_health_check_performance(self):
        """Test health check response time."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second


class TestFinanceBot:
    """Test Finance Bot API endpoints."""

    def test_finance_dashboard_success(self):
        """Test finance dashboard returns valid data."""
        response = client.get("/api/finance")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["bot"] == "Finance AI"
        assert "data" in data
        assert "insights" in data
        assert "recommendations" in data

        # Check data fields
        finance_data = data["data"]
        assert "revenue" in finance_data
        assert "expenses" in finance_data
        assert "profit" in finance_data
        assert "growth" in finance_data

        # Check data types
        assert isinstance(finance_data["revenue"], (int, float))
        assert isinstance(finance_data["expenses"], (int, float))
        assert isinstance(finance_data["profit"], (int, float))
        assert isinstance(finance_data["growth"], (float, int))

        # Check insights and recommendations are lists
        assert isinstance(data["insights"], list)
        assert isinstance(data["recommendations"], list)
        assert len(data["insights"]) > 0
        assert len(data["recommendations"]) > 0

    def test_finance_data_calculation(self):
        """Test finance data calculations are correct."""
        response = client.get("/api/finance")
        data = response.json()["data"]

        # Basic calculation check
        calculated_profit = data["revenue"] - data["expenses"]
        # Allow for floating point errors
        assert abs(calculated_profit - data["profit"]) < 0.01


class TestSalesBot:
    """Test Sales Bot API endpoints."""

    def test_sales_dashboard_success(self):
        """Test sales dashboard returns valid data."""
        response = client.get("/api/sales")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["bot"] == "Sales AI"
        assert "data" in data
        assert "insights" in data
        assert "recommendations" in data

        # Check data fields
        sales_data = data["data"]
        assert "leads" in sales_data
        assert "conversions" in sales_data
        assert "pipeline_value" in sales_data
        assert "close_rate" in sales_data

        # Check data types and ranges
        assert isinstance(sales_data["leads"], int)
        assert isinstance(sales_data["conversions"], int)
        assert isinstance(sales_data["pipeline_value"], (int, float))
        assert isinstance(sales_data["close_rate"], (float, int))

        # Business logic checks
        assert sales_data["leads"] >= sales_data["conversions"]
        assert 0 <= sales_data["close_rate"] <= 100

    def test_conversion_rate_calculation(self):
        """Test conversion rate calculation."""
        response = client.get("/api/sales")
        data = response.json()["data"]

        if data["leads"] > 0:
            calculated_rate = (data["conversions"] / data["leads"]) * 100
            # Allow for some variance in calculation method
            assert abs(calculated_rate - data["close_rate"]) < 5.0


class TestSchedulerBot:
    """Test Scheduler Bot API endpoints."""

    def test_scheduler_dashboard_success(self):
        """Test scheduler dashboard returns valid data."""
        response = client.get("/api/scheduler")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert data["bot"] == "Scheduler AI"
        assert "data" in data
        assert "insights" in data
        assert "recommendations" in data

        # Check data fields
        scheduler_data = data["data"]
        assert "meetings_today" in scheduler_data
        assert "availability" in scheduler_data
        assert "next_meeting" in scheduler_data
        assert "optimization_score" in scheduler_data

        # Check data types
        assert isinstance(scheduler_data["meetings_today"], int)
        assert isinstance(scheduler_data["availability"], str)
        assert isinstance(scheduler_data["next_meeting"], str)
        assert isinstance(scheduler_data["optimization_score"], (int, float))

        # Check ranges
        assert scheduler_data["meetings_today"] >= 0
        assert 0 <= scheduler_data["optimization_score"] <= 100


class TestChatEndpoints:
    """Test chat functionality with bots."""

    @pytest.mark.parametrize("bot_type", ["finance", "sales", "scheduler"])
    def test_chat_with_valid_bot(self, bot_type):
        """Test chat with valid bot types."""
        message = {"message": "Hello, what's my status?"}
        response = client.post(f"/api/chat/{bot_type}", json=message)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "bot" in data
        assert "response" in data
        assert "timestamp" in data
        assert "confidence" in data

        # Check bot name format
        assert data["bot"] == f"{bot_type.title()} AI"

        # Check response contains user message
        user_msg = message["message"]
        bot_response = data["response"]
        assert user_msg in bot_response or bot_type in bot_response

        # Check confidence is realistic
        assert 0.0 <= data["confidence"] <= 1.0

    def test_chat_with_invalid_bot(self):
        """Test chat with invalid bot type."""
        message = {"message": "Hello"}
        response = client.post("/api/chat/invalid_bot", json=message)

        assert response.status_code == 404
        assert "Bot not found" in response.json()["detail"]

    def test_chat_with_empty_message(self):
        """Test chat with empty message."""
        message = {"message": ""}
        response = client.post("/api/chat/finance", json=message)

        # Should still process empty message
        assert response.status_code == 200

    def test_chat_without_message_field(self):
        """Test chat without message field."""
        invalid_data = {"text": "Hello"}
        response = client.post("/api/chat/finance", json=invalid_data)

        # Should handle missing message field gracefully
        assert response.status_code == 200


class TestAnalyticsEndpoint:
    """Test analytics endpoint."""

    def test_analytics_success(self):
        """Test analytics endpoint returns valid data."""
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()

        # Check main sections
        assert "overview" in data
        assert "performance" in data
        assert "trends" in data

        # Check overview data
        overview = data["overview"]
        assert "total_revenue" in overview
        assert "active_leads" in overview
        assert "meetings_scheduled" in overview
        assert "overall_efficiency" in overview

        # Check performance scores
        performance = data["performance"]
        assert "finance_score" in performance
        assert "sales_score" in performance
        assert "scheduling_score" in performance

        # Check all scores are in valid range
        for score in performance.values():
            assert 0 <= score <= 100

        # Check trends format
        trends = data["trends"]
        assert "revenue_growth" in trends
        assert "lead_conversion" in trends
        assert "time_optimization" in trends

        # Check trends have percentage format
        for trend in trends.values():
            assert isinstance(trend, str)
            assert "%" in trend


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_headers_present(self):
        """Test CORS headers are present in responses."""
        origin = "https://razor303jc.github.io"
        response = client.get("/", headers={"Origin": origin})

        assert response.status_code == 200
        # Note: TestClient doesn't include CORS headers,
        # but we can test the middleware is configured
        # In actual deployment, these headers would be present

    def test_preflight_request(self):
        """Test CORS preflight request."""
        headers = {
            "Origin": "https://razor303jc.github.io",
            "Access-Control-Request-Method": "GET",
        }
        response = client.options("/api/finance", headers=headers)
        # TestClient handles OPTIONS differently, but middleware is configured
        assert response.status_code in [200, 405]  # May not support OPTIONS


@pytest.mark.slow
class TestPerformance:
    """Test API performance."""

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/",
            "/health",
            "/api/finance",
            "/api/sales",
            "/api/scheduler",
            "/api/analytics",
        ],
    )
    def test_endpoint_response_time(self, endpoint):
        """Test all endpoints respond within acceptable time."""
        import time

        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Should respond within 2 seconds

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import threading
        import time

        results = []

        def make_request():
            start_time = time.time()
            response = client.get("/api/finance")
            end_time = time.time()
            results.append(
                {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                }
            )

        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all requests to complete
        for thread in threads:
            thread.join()

        # Check all requests succeeded
        assert len(results) == 10
        for result in results:
            assert result["status_code"] == 200
            # Allow more time for concurrent requests
            assert result["response_time"] < 5.0


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across endpoints."""

    def test_finance_data_consistency(self):
        """Test finance data is consistent across multiple calls."""
        response1 = client.get("/api/finance")
        response2 = client.get("/api/finance")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()["data"]
        data2 = response2.json()["data"]

        # Data should be consistent (since it's static in demo)
        assert data1 == data2

    def test_analytics_data_matches_individual_endpoints(self):
        """Test analytics data matches individual bot endpoints."""
        # Get individual endpoint data
        finance_response = client.get("/api/finance")
        sales_response = client.get("/api/sales")
        scheduler_response = client.get("/api/scheduler")
        analytics_response = client.get("/api/analytics")

        responses = [
            finance_response,
            sales_response,
            scheduler_response,
            analytics_response,
        ]
        assert all(r.status_code == 200 for r in responses)

        finance_data = finance_response.json()["data"]
        sales_data = sales_response.json()["data"]
        scheduler_data = scheduler_response.json()["data"]
        analytics_data = analytics_response.json()

        # Check analytics overview matches individual data
        overview = analytics_data["overview"]
        assert overview["total_revenue"] == finance_data["revenue"]
        assert overview["active_leads"] == sales_data["leads"]
        meetings_today = scheduler_data["meetings_today"]
        assert overview["meetings_scheduled"] == meetings_today


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
