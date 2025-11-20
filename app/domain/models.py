"""Domain models using Pydantic.

This module defines the core domain models that represent the business entities
of the application. All models use Pydantic for validation and serialization.
"""

from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# User Models
# ============================================================================


class User(BaseModel):
    """User domain model.

    Represents a user in the system with authentication credentials.
    """

    email: str = Field(..., description="User's email address (unique identifier)")
    name: str = Field(..., description="User's full name")
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")

    model_config = {"from_attributes": True}

    @field_validator("email")
    @classmethod
    def validate_email_case(cls, value: str) -> str:
        """Ensure email is valid while preserving original casing."""
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError("Invalid email address") from e
        return value


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Used for user registration requests.
    """

    email: str = Field(..., description="User's email address", examples=["user@example.com"])
    name: str = Field(..., min_length=2, max_length=100, description="User's full name", examples=["John Doe"])
    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)", examples=["password123"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {"email": "user@example.com", "name": "John Doe", "password": "securepassword123"}
        }
    }

    @field_validator("email")
    @classmethod
    def validate_email_case(cls, value: str) -> str:
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError("Invalid email address") from e
        return value


class UserLogin(BaseModel):
    """Schema for user login.

    Used for authentication requests.
    """

    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "securepassword123"}}}

    @field_validator("email")
    @classmethod
    def validate_email_case(cls, value: str) -> str:
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError("Invalid email address") from e
        return value


class UserResponse(BaseModel):
    """Schema for user response.

    Used when returning user information (without password).
    """

    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
            }
        },
    }

    @field_validator("email")
    @classmethod
    def validate_email_case(cls, value: str) -> str:
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError("Invalid email address") from e
        return value


# ============================================================================
# Authentication Models
# ============================================================================


class Token(BaseModel):
    """JWT token response model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")

    model_config = {
        "json_schema_extra": {
            "example": {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}
        }
    }


class TokenData(BaseModel):
    """Token payload data model.

    Represents the decoded JWT token payload.
    """

    email: str | None = Field(default=None, description="User's email from token subject")


# ============================================================================
# Image Analysis Models
# ============================================================================


class Tag(BaseModel):
    """Image tag/label model.

    Represents a label detected by the AI service with its confidence score.
    """

    label: str = Field(..., description="Label/tag name", examples=["Dog", "Golden Retriever", "Pet"])
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1", examples=[0.98])

    model_config = {"json_schema_extra": {"example": {"label": "Dog", "confidence": 0.98}}}


class ImageAnalysisResult(BaseModel):
    """Image analysis result model.

    Contains the list of tags detected in an image.
    """

    tags: list[Tag] = Field(..., description="List of detected tags with confidence scores")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tags": [
                    {"label": "Dog", "confidence": 0.98},
                    {"label": "Golden Retriever", "confidence": 0.95},
                    {"label": "Pet", "confidence": 0.92},
                ],
                "analyzed_at": "2024-01-15T10:30:00",
            }
        }
    }


class ImageAnalysisRequest(BaseModel):
    """Image analysis request metadata.

    Used for logging and tracking analysis requests.
    """

    user_email: str = Field(..., description="Email of the user requesting the analysis")
    file_name: str = Field(..., description="Original filename of the uploaded image")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_email": "user@example.com",
                "file_name": "dog_photo.jpg",
                "file_size": 1024000,
                "content_type": "image/jpeg",
            }
        }
    }


class ImageAnalysis(BaseModel):
    """Image analysis record for persistence.

    Represents a complete analysis record stored in the database.
    """

    analysis_id: str = Field(..., description="Unique analysis identifier (UUID)")
    user_email: str = Field(..., description="Email of the user who requested the analysis")
    file_name: str = Field(..., description="Original filename of the analyzed image")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    tags: list[Tag] = Field(..., description="List of detected tags with confidence scores")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_email": "user@example.com",
                "file_name": "dog_photo.jpg",
                "file_size": 1024000,
                "content_type": "image/jpeg",
                "tags": [
                    {"label": "Dog", "confidence": 0.98},
                    {"label": "Golden Retriever", "confidence": 0.95},
                ],
                "analyzed_at": "2024-01-15T10:30:00",
            }
        },
    }
