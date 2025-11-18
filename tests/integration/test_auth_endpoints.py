"""Integration tests for authentication endpoints."""

from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domain.models import User


class TestAuthEndpoints:
    """Test suite for authentication API endpoints."""

    # ========================================================================
    # User Registration Tests
    # ========================================================================

    def test_register_success(self, client: TestClient, users_table: Any) -> None:
        """Test successful user registration."""
        user_data = {"email": "newuser@example.com", "password": "StrongPassword123!"}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["is_active"] is True
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_email(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test registration with duplicate email."""
        user_data = {"email": "duplicate@example.com", "password": "StrongPassword123!"}

        # Register first time
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Try to register again
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient) -> None:
        """Test registration with invalid email."""
        user_data = {"email": "invalid-email", "password": "StrongPassword123!"}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_weak_password(self, client: TestClient) -> None:
        """Test registration with weak password."""
        user_data = {"email": "test@example.com", "password": "123"}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self, client: TestClient) -> None:
        """Test registration with missing required fields."""
        # Missing password
        response1 = client.post("/api/v1/auth/register", json={"email": "test@example.com"})
        assert response1.status_code == 422

        # Missing email
        response2 = client.post("/api/v1/auth/register", json={"password": "StrongPassword123!"})
        assert response2.status_code == 422

        # Missing both
        response3 = client.post("/api/v1/auth/register", json={})
        assert response3.status_code == 422

    def test_register_empty_string_fields(self, client: TestClient) -> None:
        """Test registration with empty string fields."""
        user_data = {"email": "", "password": ""}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422

    # ========================================================================
    # User Login Tests
    # ========================================================================

    def test_login_success(self, client: TestClient, users_table: Any) -> None:
        """Test successful login."""
        # First register a user
        register_data = {"email": "login@example.com", "password": "StrongPassword123!"}
        client.post("/api/v1/auth/register", json=register_data)

        # Now login
        login_data = {"email": "login@example.com", "password": "StrongPassword123!"}
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client: TestClient, users_table: Any) -> None:
        """Test login with wrong password."""
        # Register user
        register_data = {"email": "user@example.com", "password": "CorrectPassword123!"}
        client.post("/api/v1/auth/register", json=register_data)

        # Try to login with wrong password
        login_data = {"email": "user@example.com", "password": "WrongPassword123!"}
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with non-existent user."""
        login_data = {"email": "nonexistent@example.com", "password": "Password123!"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_email_format(self, client: TestClient) -> None:
        """Test login with invalid email format."""
        login_data = {"email": "not-an-email", "password": "Password123!"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_missing_credentials(self, client: TestClient) -> None:
        """Test login with missing credentials."""
        # Missing password
        response1 = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response1.status_code == 422

        # Missing email
        response2 = client.post("/api/v1/auth/login", json={"password": "Password123!"})
        assert response2.status_code == 422

    # ========================================================================
    # Get Current User Tests
    # ========================================================================

    def test_get_current_user_success(self, client: TestClient, users_table: Any) -> None:
        """Test getting current user with valid token."""
        # Register and login
        register_data = {"email": "current@example.com", "password": "StrongPassword123!"}
        client.post("/api/v1/auth/register", json=register_data)

        login_response = client.post("/api/v1/auth/login", json=register_data)
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_get_current_user_no_token(self, client: TestClient) -> None:
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_get_current_user_invalid_token(self, client: TestClient) -> None:
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    def test_get_current_user_expired_token(
        self, client: TestClient, expired_token: str
    ) -> None:
        """Test getting current user with expired token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    def test_get_current_user_malformed_auth_header(self, client: TestClient) -> None:
        """Test getting current user with malformed authorization header."""
        # Missing "Bearer" prefix
        response1 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some.token.here"},
        )
        assert response1.status_code == 401

        # Wrong scheme
        response2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic some-credentials"},
        )
        assert response2.status_code == 401

    # ========================================================================
    # End-to-End Auth Flow Tests
    # ========================================================================

    def test_complete_auth_flow(self, client: TestClient, users_table: Any) -> None:
        """Test complete authentication flow: register -> login -> access protected resource."""
        email = "flow@example.com"
        password = "FlowPassword123!"

        # 1. Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Access protected endpoint
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == email

    def test_multiple_users_can_register_and_login(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that multiple users can register and login independently."""
        users = [
            {"email": "user1@example.com", "password": "Password1!"},
            {"email": "user2@example.com", "password": "Password2!"},
            {"email": "user3@example.com", "password": "Password3!"},
        ]

        tokens = []

        for user_data in users:
            # Register
            reg_response = client.post("/api/v1/auth/register", json=user_data)
            assert reg_response.status_code == 201

            # Login
            login_response = client.post("/api/v1/auth/login", json=user_data)
            assert login_response.status_code == 200
            tokens.append(login_response.json()["access_token"])

        # Verify each token works for correct user
        for i, user_data in enumerate(users):
            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {tokens[i]}"},
            )
            assert response.status_code == 200
            assert response.json()["email"] == user_data["email"]

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_register_with_special_characters_in_email(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test registration with special characters in email."""
        user_data = {"email": "user+tag@example.co.uk", "password": "StrongPassword123!"}

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]

    def test_login_case_sensitive_email(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that login email is case-sensitive."""
        register_data = {"email": "Test@Example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=register_data)

        # Try to login with different case
        login_data = {"email": "test@example.com", "password": "Password123!"}
        response = client.post("/api/v1/auth/login", json=login_data)

        # Should fail because DynamoDB is case-sensitive
        assert response.status_code == 401

    def test_token_can_be_reused(self, client: TestClient, users_table: Any) -> None:
        """Test that a valid token can be used multiple times."""
        register_data = {"email": "reuse@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=register_data)

        login_response = client.post("/api/v1/auth/login", json=register_data)
        token = login_response.json()["access_token"]

        # Use token multiple times
        for _ in range(3):
            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200