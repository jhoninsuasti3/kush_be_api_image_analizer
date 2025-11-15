"""Custom exceptions for the application.

This module defines all custom exceptions used throughout the application.
All exceptions inherit from a base exception class for consistent error handling.
"""


class AppException(Exception):
    """Base exception for all application exceptions.

    All custom exceptions should inherit from this class.
    This allows for easy exception handling at the application level.
    """

    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code associated with this error.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================


class AuthenticationException(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize the exception with 401 Unauthorized status."""
        super().__init__(message, status_code=401)


class InvalidCredentialsException(AuthenticationException):
    """Raised when credentials are invalid."""

    def __init__(self, message: str = "Invalid email or password") -> None:
        """Initialize the exception."""
        super().__init__(message)


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid or expired."""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        """Initialize the exception."""
        super().__init__(message)


class UnauthorizedException(AppException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized to perform this action") -> None:
        """Initialize the exception with 403 Forbidden status."""
        super().__init__(message, status_code=403)


# ============================================================================
# User Exceptions
# ============================================================================


class UserNotFoundException(AppException):
    """Raised when a user is not found."""

    def __init__(self, message: str = "User not found") -> None:
        """Initialize the exception with 404 Not Found status."""
        super().__init__(message, status_code=404)


class UserAlreadyExistsException(AppException):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str = "User with this email already exists") -> None:
        """Initialize the exception with 409 Conflict status."""
        super().__init__(message, status_code=409)


class InactiveUserException(AppException):
    """Raised when attempting to authenticate an inactive user."""

    def __init__(self, message: str = "User account is inactive") -> None:
        """Initialize the exception with 403 Forbidden status."""
        super().__init__(message, status_code=403)


# ============================================================================
# File Upload Exceptions
# ============================================================================


class FileValidationException(AppException):
    """Raised when file validation fails."""

    def __init__(self, message: str = "File validation failed") -> None:
        """Initialize the exception with 400 Bad Request status."""
        super().__init__(message, status_code=400)


class InvalidFileTypeException(FileValidationException):
    """Raised when file type is not allowed."""

    def __init__(self, message: str = "File type not allowed") -> None:
        """Initialize the exception."""
        super().__init__(message)


class FileTooLargeException(AppException):
    """Raised when file size exceeds the limit."""

    def __init__(self, message: str = "File size exceeds the maximum allowed size") -> None:
        """Initialize the exception with 413 Payload Too Large status."""
        super().__init__(message, status_code=413)


class InvalidImageFormatException(FileValidationException):
    """Raised when image format is invalid or corrupted."""

    def __init__(self, message: str = "Invalid or corrupted image file") -> None:
        """Initialize the exception."""
        super().__init__(message)


# ============================================================================
# AI Service Exceptions
# ============================================================================


class AIServiceException(AppException):
    """Raised when AI service encounters an error."""

    def __init__(self, message: str = "AI service error") -> None:
        """Initialize the exception with 502 Bad Gateway status."""
        super().__init__(message, status_code=502)


class AIServiceUnavailableException(AppException):
    """Raised when AI service is unavailable."""

    def __init__(self, message: str = "AI service is currently unavailable") -> None:
        """Initialize the exception with 503 Service Unavailable status."""
        super().__init__(message, status_code=503)


class AIServiceRateLimitException(AppException):
    """Raised when AI service rate limit is exceeded."""

    def __init__(self, message: str = "AI service rate limit exceeded") -> None:
        """Initialize the exception with 429 Too Many Requests status."""
        super().__init__(message, status_code=429)


class NoLabelsDetectedException(AppException):
    """Raised when AI service doesn't detect any labels in the image."""

    def __init__(self, message: str = "No labels detected in the image") -> None:
        """Initialize the exception with 422 Unprocessable Entity status."""
        super().__init__(message, status_code=422)


# ============================================================================
# Database Exceptions
# ============================================================================


class DatabaseException(AppException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database error") -> None:
        """Initialize the exception with 500 Internal Server Error status."""
        super().__init__(message, status_code=500)


class DatabaseConnectionException(AppException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database") -> None:
        """Initialize the exception with 503 Service Unavailable status."""
        super().__init__(message, status_code=503)


# ============================================================================
# Validation Exceptions
# ============================================================================


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation error") -> None:
        """Initialize the exception with 422 Unprocessable Entity status."""
        super().__init__(message, status_code=422)
