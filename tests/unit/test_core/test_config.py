"""Unit tests for app.core.config module."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_settings_default_values(self) -> None:
        """Test that settings have expected default values."""
        # Create settings without loading from .env to test defaults
        settings = Settings(_env_file=None)

        assert settings.app_name == "Kush Image Analyzer API"
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.aws_region == "us-east-1"
        assert settings.jwt_algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        assert settings.max_file_size_mb == 5
        assert settings.log_level == "INFO"

    def test_max_file_size_bytes_property(self) -> None:
        """Test max_file_size_bytes computed property."""
        settings = Settings(max_file_size_mb=5)

        assert settings.max_file_size_bytes == 5 * 1024 * 1024

    def test_allowed_extensions_list_property(self) -> None:
        """Test allowed_extensions_list computed property."""
        settings = Settings(allowed_extensions="jpg,jpeg,png,webp")

        extensions = settings.allowed_extensions_list

        assert extensions == ["jpg", "jpeg", "png", "webp"]

    def test_allowed_extensions_list_with_spaces(self) -> None:
        """Test allowed_extensions_list handles spaces correctly."""
        settings = Settings(allowed_extensions="jpg, jpeg , png,  webp")

        extensions = settings.allowed_extensions_list

        assert extensions == ["jpg", "jpeg", "png", "webp"]

    def test_cors_origins_list_property(self) -> None:
        """Test cors_origins_list computed property."""
        settings = Settings(cors_origins="http://localhost:3000,http://localhost:5173")

        origins = settings.cors_origins_list

        assert origins == ["http://localhost:3000", "http://localhost:5173"]

    def test_is_production_property(self) -> None:
        """Test is_production property."""
        dev_settings = Settings(environment="development")
        prod_settings = Settings(environment="production")

        assert dev_settings.is_production is False
        assert prod_settings.is_production is True

    def test_is_development_property(self) -> None:
        """Test is_development property."""
        dev_settings = Settings(environment="development")
        prod_settings = Settings(environment="production")

        assert dev_settings.is_development is True
        assert prod_settings.is_development is False

    def test_is_sentry_enabled_property_when_dsn_is_set(self) -> None:
        """Test is_sentry_enabled returns True when DSN is set."""
        settings = Settings(sentry_dsn="https://example.sentry.io/123456")

        assert settings.is_sentry_enabled is True

    def test_is_sentry_enabled_property_when_dsn_is_empty(self) -> None:
        """Test is_sentry_enabled returns False when DSN is empty."""
        settings = Settings(sentry_dsn="")

        assert settings.is_sentry_enabled is False

    def test_jwt_secret_key_validation_fails_when_too_short(self) -> None:
        """Test that JWT secret key validation fails when key is too short."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(jwt_secret_key="short")

        errors = exc_info.value.errors()
        assert any("at least 32 characters" in str(error) for error in errors)

    def test_jwt_secret_key_validation_passes_when_long_enough(self) -> None:
        """Test that JWT secret key validation passes when key is long enough."""
        long_key = "a" * 32

        settings = Settings(jwt_secret_key=long_key)

        assert settings.jwt_secret_key == long_key

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self) -> None:
        """Test that get_settings returns the same instance (cached)."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the exact same instance due to lru_cache
        assert settings1 is settings2

    def test_environment_validation_accepts_valid_values(self) -> None:
        """Test that environment field accepts valid literal values."""
        dev_settings = Settings(environment="development")
        staging_settings = Settings(environment="staging")
        prod_settings = Settings(environment="production")

        assert dev_settings.environment == "development"
        assert staging_settings.environment == "staging"
        assert prod_settings.environment == "production"

    def test_log_level_validation_accepts_valid_values(self) -> None:
        """Test that log_level field accepts valid literal values."""
        settings_debug = Settings(log_level="DEBUG")
        settings_info = Settings(log_level="INFO")
        settings_error = Settings(log_level="ERROR")

        assert settings_debug.log_level == "DEBUG"
        assert settings_info.log_level == "INFO"
        assert settings_error.log_level == "ERROR"
