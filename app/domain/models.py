"""Domain models using Pydantic.

This module defines the core domain models that represent the business entities
of the application. All models use Pydantic for validation and serialization.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# ============================================================================
# User Models
# ============================================================================


class User(BaseModel):
    """User domain model.

    Represents a user in the system with authentication credentials.
    """

    email: EmailStr = Field(..., description="User's email address (unique identifier)")
    hashed_password: str = Field(..., description="Bcrypt hashed password")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Used for user registration requests.
    """

    email: EmailStr = Field(..., description="User's email address", examples=["user@example.com"])
    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)", examples=["password123"]
    )

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "securepassword123"}}}


class UserLogin(BaseModel):
    """Schema for user login.

    Used for authentication requests.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "securepassword123"}}}


class UserResponse(BaseModel):
    """Schema for user response.

    Used when returning user information (without password).
    """

    email: EmailStr = Field(..., description="User's email address")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {"email": "user@example.com", "is_active": True, "created_at": "2024-01-15T10:30:00"}
        },
    }


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
