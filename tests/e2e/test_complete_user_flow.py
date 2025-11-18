"""End-to-end tests for complete user flows."""

from io import BytesIO
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.domain.models import ImageAnalysisResult, Tag


class TestCompleteUserFlow:
    """Test suite for complete end-to-end user flows."""

    # ========================================================================
    # Complete Image Analysis Flow
    # ========================================================================

    def test_complete_image_analysis_flow(self, client: TestClient, users_table: Any) -> None:
        """Test complete flow: register -> login -> analyze image."""
        # Step 1: Register a new user
        register_data = {"email": "e2e@example.com", "password": "E2EPassword123!"}
        register_response = client.post("/api/v1/auth/register", json=register_data)

        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == "e2e@example.com"
        assert user_data["is_active"] is True

        # Step 2: Login with the user
        login_response = client.post("/api/v1/auth/login", json=register_data)

        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        token = token_data["access_token"]

        # Step 3: Verify token works by getting current user
        me_response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == 200
        current_user = me_response.json()
        assert current_user["email"] == "e2e@example.com"

        # Step 4: Create and upload an image
        img = Image.new("RGB", (200, 200), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"file": ("test_e2e.jpg", img_bytes, "image/jpeg")}

        # Mock the AI service for E2E test
        mock_result = ImageAnalysisResult(
            tags=[
                Tag(label="Sky", confidence=0.96),
                Tag(label="Blue", confidence=0.93),
                Tag(label="Nature", confidence=0.88),
            ]
        )

        with patch(
            "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
        ) as mock_analyze:
            mock_analyze.return_value = mock_result

            # Step 5: Analyze the image
            analyze_response = client.post(
                "/api/v1/analyze",
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )

            assert analyze_response.status_code == 200
            analysis_data = analyze_response.json()
            assert "tags" in analysis_data
            assert len(analysis_data["tags"]) == 3
            assert analysis_data["tags"][0]["label"] == "Sky"
            assert analysis_data["tags"][0]["confidence"] == 0.96

    def test_multiple_users_complete_flow(self, client: TestClient, users_table: Any) -> None:
        """Test complete flow with multiple users analyzing images."""
        users = [
            {"email": "user1@flow.com", "password": "User1Password!"},
            {"email": "user2@flow.com", "password": "User2Password!"},
            {"email": "user3@flow.com", "password": "User3Password!"},
        ]

        mock_results = [
            ImageAnalysisResult(tags=[Tag(label="Cat", confidence=0.95)]),
            ImageAnalysisResult(tags=[Tag(label="Dog", confidence=0.92)]),
            ImageAnalysisResult(tags=[Tag(label="Bird", confidence=0.89)]),
        ]

        for i, user_data in enumerate(users):
            # Register
            register_response = client.post("/api/v1/auth/register", json=user_data)
            assert register_response.status_code == 201

            # Login
            login_response = client.post("/api/v1/auth/login", json=user_data)
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]

            # Analyze image
            img = Image.new("RGB", (100, 100), color=["red", "green", "blue"][i])
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"file": (f"image_{i}.jpg", img_bytes, "image/jpeg")}

            with patch(
                "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
            ) as mock_analyze:
                mock_analyze.return_value = mock_results[i]

                analyze_response = client.post(
                    "/api/v1/analyze",
                    files=files,
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert analyze_response.status_code == 200
                data = analyze_response.json()
                assert data["tags"][0]["label"] == mock_results[i].tags[0].label

    # ========================================================================
    # Authentication Error Flows
    # ========================================================================

    def test_analyze_without_registration(self, client: TestClient) -> None:
        """Test that analyzing without registration fails."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

        # Try to analyze without authentication
        response = client.post("/api/v1/analyze", files=files)

        assert response.status_code == 401

    def test_analyze_with_wrong_credentials(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that analyzing with wrong credentials fails."""
        # Register user
        register_data = {"email": "correct@example.com", "password": "CorrectPassword!"}
        client.post("/api/v1/auth/register", json=register_data)

        # Try to login with wrong password
        wrong_login = {"email": "correct@example.com", "password": "WrongPassword!"}
        login_response = client.post("/api/v1/auth/login", json=wrong_login)

        assert login_response.status_code == 401

    # ========================================================================
    # File Validation Error Flows
    # ========================================================================

    def test_complete_flow_with_invalid_file(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test complete flow with invalid file type."""
        # Register and login
        user_data = {"email": "invalid_file@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)

        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        # Try to upload invalid file type
        text_file = BytesIO(b"This is not an image")
        files = {"file": ("document.txt", text_file, "text/plain")}

        response = client.post(
            "/api/v1/analyze",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    def test_complete_flow_with_large_file(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test complete flow with file exceeding size limit."""
        # Register and login
        user_data = {"email": "large_file@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)

        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        # Create large file (>5MB)
        large_img = Image.new("RGB", (3000, 3000), color="white")
        img_bytes = BytesIO()
        large_img.save(img_bytes, format="JPEG", quality=100)
        img_bytes.seek(0)

        files = {"file": ("large.jpg", img_bytes, "image/jpeg")}

        response = client.post(
            "/api/v1/analyze",
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    # ========================================================================
    # Multiple Analysis Sessions
    # ========================================================================

    def test_user_can_analyze_multiple_images(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that a user can analyze multiple images in sequence."""
        # Register and login
        user_data = {"email": "multi@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)

        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        # Analyze multiple images
        colors = ["red", "green", "blue", "yellow", "purple"]
        labels = ["Apple", "Grass", "Sky", "Sun", "Flower"]

        for i, (color, label) in enumerate(zip(colors, labels)):
            img = Image.new("RGB", (100, 100), color=color)
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"file": (f"image_{i}.jpg", img_bytes, "image/jpeg")}

            mock_result = ImageAnalysisResult(
                tags=[Tag(label=label, confidence=0.90 + i * 0.01)]
            )

            with patch(
                "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
            ) as mock_analyze:
                mock_analyze.return_value = mock_result

                response = client.post(
                    "/api/v1/analyze",
                    files=files,
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["tags"][0]["label"] == label

    # ========================================================================
    # Session Persistence Tests
    # ========================================================================

    def test_token_persists_across_multiple_requests(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that token can be reused for multiple requests."""
        # Register and login
        user_data = {"email": "persist@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)

        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        # Use the same token for multiple requests
        for _ in range(5):
            # Check user info
            me_response = client.get(
                "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
            )
            assert me_response.status_code == 200

            # Analyze image
            img = Image.new("RGB", (50, 50), color="red")
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

            mock_result = ImageAnalysisResult(tags=[Tag(label="Test", confidence=0.95)])

            with patch(
                "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
            ) as mock_analyze:
                mock_analyze.return_value = mock_result

                analyze_response = client.post(
                    "/api/v1/analyze",
                    files=files,
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert analyze_response.status_code == 200

    # ========================================================================
    # Different Image Formats Flow
    # ========================================================================

    def test_analyze_different_image_formats(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test analyzing different image formats (JPEG, PNG, WebP)."""
        # Register and login
        user_data = {"email": "formats@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)

        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        formats = [
            ("JPEG", "image/jpeg", "test.jpg"),
            ("PNG", "image/png", "test.png"),
            ("WEBP", "image/webp", "test.webp"),
        ]

        for img_format, content_type, filename in formats:
            img = Image.new("RGB", (100, 100), color="blue")
            img_bytes = BytesIO()
            img.save(img_bytes, format=img_format)
            img_bytes.seek(0)

            files = {"file": (filename, img_bytes, content_type)}

            mock_result = ImageAnalysisResult(
                tags=[Tag(label=f"{img_format}_Image", confidence=0.94)]
            )

            with patch(
                "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
            ) as mock_analyze:
                mock_analyze.return_value = mock_result

                response = client.post(
                    "/api/v1/analyze",
                    files=files,
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data["tags"]) > 0

    # ========================================================================
    # Health Check Integration
    # ========================================================================

    def test_health_checks_during_user_flow(
        self, client: TestClient, users_table: Any
    ) -> None:
        """Test that health checks work during normal user flow."""
        # Check health before anything
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

        # Check readiness
        ready_response = client.get("/api/v1/ready")
        assert ready_response.status_code == 200

        # Register and login
        user_data = {"email": "health@example.com", "password": "Password123!"}
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json=user_data)
        token = login_response.json()["access_token"]

        # Check health again
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200

        # Analyze image
        img = Image.new("RGB", (100, 100), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

        mock_result = ImageAnalysisResult(tags=[Tag(label="Green", confidence=0.91)])

        with patch(
            "app.infrastructure.ai.google_vision_service.GoogleVisionService.analyze_image"
        ) as mock_analyze:
            mock_analyze.return_value = mock_result

            analyze_response = client.post(
                "/api/v1/analyze",
                files=files,
                headers={"Authorization": f"Bearer {token}"},
            )

            assert analyze_response.status_code == 200

        # Final health check
        final_health = client.get("/api/v1/health")
        assert final_health.status_code == 200