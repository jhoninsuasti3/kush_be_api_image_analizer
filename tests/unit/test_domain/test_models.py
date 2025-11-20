"""Unit tests for app.domain.models module."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domain.models import (
    ImageAnalysisRequest,
    ImageAnalysisResult,
    Tag,
    Token,
    TokenData,
    User,
    UserCreate,
    UserLogin,
    UserResponse,
)


class TestUserModels:
    """Tests for User-related models."""

    def test_user_model_creation(self) -> None:
        """Test creating a User model with valid data."""
        user = User(email="test@example.com", name="Test User", hashed_password="hashed_password_here")

        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.hashed_password == "hashed_password_here"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)

    def test_user_model_with_invalid_email(self) -> None:
        """Test that User model validates email format."""
        with pytest.raises(ValidationError):
            User(email="invalid-email", name="Test User", hashed_password="hashed_password")

    def test_user_create_model(self) -> None:
        """Test creating a UserCreate model."""
        user_create = UserCreate(email="test@example.com", name="Test User", password="password123")

        assert user_create.email == "test@example.com"
        assert user_create.name == "Test User"
        assert user_create.password == "password123"

    def test_user_create_password_min_length(self) -> None:
        """Test that UserCreate validates password minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", name="Test User", password="short")

        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(error) for error in errors)

    def test_user_login_model(self) -> None:
        """Test creating a UserLogin model."""
        user_login = UserLogin(email="test@example.com", password="password123")

        assert user_login.email == "test@example.com"
        assert user_login.password == "password123"

    def test_user_response_model(self) -> None:
        """Test creating a UserResponse model."""
        now = datetime.utcnow()
        user_response = UserResponse(email="test@example.com", name="Test User", is_active=True, created_at=now)

        assert user_response.email == "test@example.com"
        assert user_response.name == "Test User"
        assert user_response.is_active is True
        assert user_response.created_at == now


class TestAuthenticationModels:
    """Tests for authentication-related models."""

    def test_token_model(self) -> None:
        """Test creating a Token model."""
        token = Token(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"

    def test_token_data_model(self) -> None:
        """Test creating a TokenData model."""
        token_data = TokenData(email="test@example.com")

        assert token_data.email == "test@example.com"

    def test_token_data_model_with_none(self) -> None:
        """Test creating a TokenData model with None email."""
        token_data = TokenData()

        assert token_data.email is None


class TestImageAnalysisModels:
    """Tests for image analysis-related models."""

    def test_tag_model(self) -> None:
        """Test creating a Tag model."""
        tag = Tag(label="Dog", confidence=0.98)

        assert tag.label == "Dog"
        assert tag.confidence == 0.98

    def test_tag_model_confidence_validation_min(self) -> None:
        """Test that Tag model validates confidence minimum value."""
        with pytest.raises(ValidationError):
            Tag(label="Dog", confidence=-0.1)

    def test_tag_model_confidence_validation_max(self) -> None:
        """Test that Tag model validates confidence maximum value."""
        with pytest.raises(ValidationError):
            Tag(label="Dog", confidence=1.1)

    def test_tag_model_confidence_at_boundaries(self) -> None:
        """Test that Tag model accepts confidence at 0.0 and 1.0."""
        tag_min = Tag(label="Test", confidence=0.0)
        tag_max = Tag(label="Test", confidence=1.0)

        assert tag_min.confidence == 0.0
        assert tag_max.confidence == 1.0

    def test_image_analysis_result_model(self) -> None:
        """Test creating an ImageAnalysisResult model."""
        tags = [
            Tag(label="Dog", confidence=0.98),
            Tag(label="Golden Retriever", confidence=0.95),
            Tag(label="Pet", confidence=0.92),
        ]

        result = ImageAnalysisResult(tags=tags)

        assert len(result.tags) == 3
        assert result.tags[0].label == "Dog"
        assert result.tags[1].label == "Golden Retriever"
        assert result.tags[2].label == "Pet"
        assert isinstance(result.analyzed_at, datetime)

    def test_image_analysis_result_empty_tags(self) -> None:
        """Test creating an ImageAnalysisResult with empty tags list."""
        result = ImageAnalysisResult(tags=[])

        assert len(result.tags) == 0

    def test_image_analysis_request_model(self) -> None:
        """Test creating an ImageAnalysisRequest model."""
        request = ImageAnalysisRequest(
            user_email="test@example.com", file_name="dog.jpg", file_size=1024000, content_type="image/jpeg"
        )

        assert request.user_email == "test@example.com"
        assert request.file_name == "dog.jpg"
        assert request.file_size == 1024000
        assert request.content_type == "image/jpeg"
