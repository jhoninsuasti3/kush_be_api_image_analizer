"""Application configuration using Pydantic Settings.

This module centralizes all configuration for the application, loading values
from environment variables with validation and type checking.
"""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Uses Pydantic for validation and type checking.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================================
    # Application Settings
    # ============================================================================
    app_name: str = Field(default="Kush Image Analyzer API", description="Application name")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # ============================================================================
    # AWS Configuration
    # ============================================================================
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")

    # DynamoDB
    dynamodb_users_table: str = Field(
        default="kush-users-dev",
        description="DynamoDB users table name",
        validation_alias=AliasChoices("dynamodb_users_table", "dynamodb_table_name"),
    )
    dynamodb_analysis_table: str = Field(
        default="kush-image-analysis-dev",
        description="DynamoDB image analysis table name",
    )
    dynamodb_endpoint_url: str | None = Field(
        default=None, description="DynamoDB endpoint URL (for local development)"
    )

    # ============================================================================
    # Google Cloud Vision Configuration
    # ============================================================================
    google_application_credentials: str = Field(
        default="", description="Path to Google Cloud service account JSON file"
    )
    google_cloud_project: str = Field(default="", description="Google Cloud project ID")
    google_api_key: str = Field(default="", description="Google API key (alternative to service account)")

    # ============================================================================
    # JWT Authentication
    # ============================================================================
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production-min-32-chars",
        description="Secret key for signing JWT tokens",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        """Validate JWT secret key length."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    # ============================================================================
    # File Upload Limits
    # ============================================================================
    max_file_size_mb: int = Field(default=5, description="Maximum file size in megabytes")
    allowed_extensions: str = Field(default="jpg,jpeg,png,webp", description="Allowed file extensions")

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Get allowed extensions as a list."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    # ============================================================================
    # Logging Configuration
    # ============================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Log level"
    )
    log_format: Literal["json", "console"] = Field(default="json", description="Log format")

    # ============================================================================
    # CORS Configuration
    # ============================================================================
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173", description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS requests")

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ============================================================================
    # API Documentation
    # ============================================================================
    enable_docs: bool = Field(default=True, description="Enable API documentation")
    docs_url: str = Field(default="/docs", description="API docs URL path")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL path")

    # ============================================================================
    # Observability (Optional)
    # ============================================================================
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    sentry_environment: str = Field(default="development", description="Sentry environment")
    sentry_traces_sample_rate: float = Field(default=0.1, description="Sentry traces sample rate")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_sentry_enabled(self) -> bool:
        """Check if Sentry is enabled."""
        return bool(self.sentry_dsn)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    This function uses lru_cache to ensure we only load settings once
    during the application lifecycle.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
