"""Integration tests for health check endpoints."""

from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test suite for health check API endpoints."""

    # ========================================================================
    # Basic Health Check Tests
    # ========================================================================

    def test_health_check_success(self, client: TestClient) -> None:
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_check_no_authentication_required(self, client: TestClient) -> None:
        """Test that health check doesn't require authentication."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200

    # ========================================================================
    # Readiness Check Tests
    # ========================================================================

    def test_readiness_check_success(self, client: TestClient, users_table: Any) -> None:
        """Test readiness check with healthy dependencies."""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["database"] == "healthy"

    def test_readiness_check_database_connection(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that readiness check verifies database connection."""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()
        assert "database" in data["checks"]
        assert data["checks"]["database"] == "healthy"

    def test_readiness_check_no_authentication_required(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that readiness check doesn't require authentication."""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200

    def test_readiness_check_database_failure(self, client: TestClient) -> None:
        """Test readiness check when database is unavailable."""
        with patch("app.infrastructure.persistence.dynamodb_client.get_users_table") as mock_get_table:
            mock_get_table.side_effect = Exception("Database connection failed")

            response = client.get("/api/v1/ready")

            # Should still return 503 or indicate unhealthy state
            # depending on implementation
            assert response.status_code in [200, 503]
            if response.status_code == 200:
                data = response.json()
                assert data["checks"]["database"] == "unhealthy"
            else:
                data = response.json()
                assert data["status"] == "not ready"

    # ========================================================================
    # Response Format Tests
    # ========================================================================

    def test_health_check_response_format(self, client: TestClient) -> None:
        """Test health check response format."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)

    def test_readiness_check_response_format(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test readiness check response format."""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert isinstance(data, dict)
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    # ========================================================================
    # Multiple Requests Tests
    # ========================================================================

    def test_health_check_multiple_requests(self, client: TestClient) -> None:
        """Test that health check can handle multiple requests."""
        for _ in range(5):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_readiness_check_multiple_requests(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that readiness check can handle multiple requests."""
        for _ in range(5):
            response = client.get("/api/v1/ready")
            assert response.status_code == 200
            assert response.json()["status"] == "ready"

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_health_endpoints_accessible_from_root(self, client: TestClient) -> None:
        """Test that health endpoints are accessible."""
        # Both endpoints should be accessible
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

    def test_health_check_returns_quickly(self, client: TestClient) -> None:
        """Test that health check responds quickly."""
        import time

        start = time.time()
        response = client.get("/api/v1/health")
        duration = time.time() - start

        assert response.status_code == 200
        # Should respond in less than 1 second
        assert duration < 1.0

    def test_health_check_consistent_response(self, client: TestClient) -> None:
        """Test that health check returns consistent responses."""
        response1 = client.get("/api/v1/health")
        response2 = client.get("/api/v1/health")

        assert response1.status_code == response2.status_code
        assert response1.json()["status"] == response2.json()["status"]