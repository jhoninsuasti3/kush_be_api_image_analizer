"""Global test configuration and fixtures."""

import os
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import boto3
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from moto import mock_aws

from app.core.config import Settings
from app.domain.models import User, UserCreate
from app.infrastructure.persistence.dynamodb_client import get_users_table
from app.main import app

# Initialize Faker
fake = Faker()


# ============================================================================
# Environment Setup
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Set up test environment variables."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-purposes-only"
    os.environ["DYNAMODB_TABLE_NAME"] = "test-users-table"
    os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
    yield
    # Clean up is automatic


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings instance."""
    return Settings(
        app_name="Test Image Analyzer API",
        environment="test",
        debug=True,
        jwt_secret_key="test-secret-key-for-testing-purposes-only",
        dynamodb_table_name="test-users-table",
        aws_region="us-east-1",
    )


# ============================================================================
# FastAPI Client Fixtures
# ============================================================================


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[TestClient, None]:
    """Create async FastAPI test client."""
    async with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# AWS DynamoDB Fixtures
# ============================================================================


@pytest.fixture
def aws_credentials() -> None:
    """Mock AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def dynamodb_mock(aws_credentials: None) -> Generator[Any, None, None]:
    """Create mocked DynamoDB instance."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create users table
        table = dynamodb.create_table(
            TableName="test-users-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName="test-users-table")

        yield dynamodb


@pytest.fixture
def users_table(dynamodb_mock: Any) -> Any:
    """Get users table instance."""
    return get_users_table()


# ============================================================================
# User Fixtures
# ============================================================================


@pytest.fixture
def user_create_data() -> dict[str, Any]:
    """Create user registration data."""
    return {"email": fake.email(), "password": "StrongPassword123!"}


@pytest.fixture
def user_create_model(user_create_data: dict[str, Any]) -> UserCreate:
    """Create UserCreate model."""
    return UserCreate(**user_create_data)


@pytest.fixture
def valid_user() -> User:
    """Create a valid user instance."""
    return User(
        email=fake.email(),
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyAJ3xIqP4iq",  # "password123"
        is_active=True,
    )


@pytest.fixture
def inactive_user() -> User:
    """Create an inactive user instance."""
    return User(
        email=fake.email(),
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyAJ3xIqP4iq",
        is_active=False,
    )


@pytest.fixture
def test_user_credentials() -> dict[str, str]:
    """Create test user credentials for login."""
    return {"email": "test@example.com", "password": "password123"}


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def valid_token(valid_user: User) -> str:
    """Create a valid JWT token for testing."""
    from app.core.security import create_token_for_user

    return create_token_for_user(valid_user)


@pytest.fixture
def expired_token() -> str:
    """Create an expired JWT token for testing."""
    from datetime import timedelta

    from app.core.security import create_access_token

    # Create token that expired 1 hour ago
    expires_delta = timedelta(hours=-1)
    return create_access_token(data={"sub": "test@example.com"}, expires_delta=expires_delta)


@pytest.fixture
def invalid_token() -> str:
    """Create an invalid JWT token."""
    return "invalid.jwt.token"


@pytest.fixture
def auth_headers(valid_token: str) -> dict[str, str]:
    """Create authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


# ============================================================================
# File Upload Fixtures
# ============================================================================


@pytest.fixture
def valid_image_file() -> dict[str, Any]:
    """Create a valid image file for upload."""
    from io import BytesIO

    from PIL import Image

    # Create a simple 100x100 red image
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    return {"file": ("test_image.jpg", img_bytes, "image/jpeg")}


@pytest.fixture
def large_image_file() -> dict[str, Any]:
    """Create a large image file (>5MB) for upload."""
    from io import BytesIO

    from PIL import Image

    # Create a large image that exceeds 5MB
    img = Image.new("RGB", (3000, 3000), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG", quality=100)
    img_bytes.seek(0)

    return {"file": ("large_image.jpg", img_bytes, "image/jpeg")}


@pytest.fixture
def invalid_file_type() -> dict[str, Any]:
    """Create a file with invalid type."""
    from io import BytesIO

    content = b"This is a text file, not an image"
    file_bytes = BytesIO(content)

    return {"file": ("test.txt", file_bytes, "text/plain")}


@pytest.fixture
def corrupted_image_file() -> dict[str, Any]:
    """Create a corrupted image file."""
    from io import BytesIO

    # Create a file with .jpg extension but invalid content
    content = b"Not a valid image content"
    file_bytes = BytesIO(content)

    return {"file": ("corrupted.jpg", file_bytes, "image/jpeg")}


# ============================================================================
# Google Vision Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_google_vision_client() -> MagicMock:
    """Create a mocked Google Vision client."""
    mock_client = MagicMock()

    # Mock successful label detection response
    mock_label = MagicMock()
    mock_label.description = "Cat"
    mock_label.score = 0.95

    mock_response = MagicMock()
    mock_response.label_annotations = [mock_label]

    mock_client.label_detection.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_vision_response_multiple_labels() -> list[dict[str, Any]]:
    """Create mock response with multiple labels."""
    return [
        {"description": "Cat", "score": 0.95},
        {"description": "Animal", "score": 0.92},
        {"description": "Pet", "score": 0.88},
        {"description": "Mammal", "score": 0.85},
    ]


@pytest.fixture
def mock_vision_response_no_labels() -> list[dict[str, Any]]:
    """Create mock response with no labels."""
    return []


@pytest.fixture(scope="session", autouse=True)
def mock_google_vision_client_globally() -> Generator[None, None, None]:
    """Mock Google Vision client globally for all tests to avoid authentication errors."""
    with patch("app.infrastructure.ai.google_vision_service.vision.ImageAnnotatorClient") as mock_client_class:
        # Create a mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Setup default response for label detection
        mock_label = MagicMock()
        mock_label.description = "Test"
        mock_label.score = 0.95

        mock_response = MagicMock()
        mock_response.label_annotations = [mock_label]
        mock_response.error.message = ""

        mock_client.label_detection.return_value = mock_response

        yield


# ============================================================================
# Factory Fixtures
# ============================================================================


@pytest.fixture
def user_factory() -> type:
    """Factory for creating test users."""

    class UserFactory:
        @staticmethod
        def create(**kwargs: Any) -> User:
            """Create a user with optional overrides."""
            defaults = {
                "email": fake.email(),
                "name": fake.name(),
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyAJ3xIqP4iq",
                "is_active": True,
            }
            defaults.update(kwargs)
            return User(**defaults)

        @staticmethod
        def create_batch(count: int, **kwargs: Any) -> list[User]:
            """Create multiple users."""
            return [UserFactory.create(**kwargs) for _ in range(count)]

    return UserFactory


@pytest.fixture
def image_analysis_result_factory() -> type:
    """Factory for creating image analysis results."""

    class ImageAnalysisResultFactory:
        @staticmethod
        def create(num_tags: int = 3) -> dict[str, Any]:
            """Create image analysis result with specified number of tags."""
            from app.domain.models import ImageAnalysisResult, Tag

            tags = [
                Tag(label=fake.word().capitalize(), confidence=fake.pyfloat(min_value=0.5, max_value=1.0))
                for _ in range(num_tags)
            ]

            return ImageAnalysisResult(tags=tags).model_dump()

    return ImageAnalysisResultFactory


# ============================================================================
# Database Setup/Teardown Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_db(users_table: Any) -> Generator[None, None, None]:
    """Reset database before each test."""
    # Clean up before test
    scan = users_table.scan()
    with users_table.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"email": item["email"]})

    yield

    # Clean up after test
    scan = users_table.scan()
    with users_table.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"email": item["email"]})
