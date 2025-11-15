"""Domain ports (interfaces) for dependency inversion.

This module defines abstract base classes (ABCs) that represent contracts
for external services. This allows for dependency inversion and makes the
domain layer independent of infrastructure implementations.

Following the Ports & Adapters (Hexagonal) architecture pattern.
"""

from abc import ABC, abstractmethod

from app.domain.models import ImageAnalysisResult, User

# ============================================================================
# Repository Ports
# ============================================================================


class IUserRepository(ABC):
    """Abstract interface for user repository.

    This port defines the contract for user persistence operations.
    Infrastructure layer will provide concrete implementations (e.g., DynamoDB).
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: The user to create.

        Returns:
            User: The created user.

        Raises:
            UserAlreadyExistsException: If a user with this email already exists.
            DatabaseException: If database operation fails.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email.

        Args:
            email: The user's email address.

        Returns:
            User | None: The user if found, None otherwise.

        Raises:
            DatabaseException: If database operation fails.
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: The user with updated information.

        Returns:
            User: The updated user.

        Raises:
            UserNotFoundException: If the user doesn't exist.
            DatabaseException: If database operation fails.
        """
        pass

    @abstractmethod
    async def delete(self, email: str) -> bool:
        """Delete a user by email.

        Args:
            email: The user's email address.

        Returns:
            bool: True if the user was deleted, False if not found.

        Raises:
            DatabaseException: If database operation fails.
        """
        pass

    @abstractmethod
    async def exists(self, email: str) -> bool:
        """Check if a user exists by email.

        Args:
            email: The user's email address.

        Returns:
            bool: True if the user exists, False otherwise.

        Raises:
            DatabaseException: If database operation fails.
        """
        pass


# ============================================================================
# AI Service Ports
# ============================================================================


class IAIService(ABC):
    """Abstract interface for AI/ML image analysis service.

    This port defines the contract for image analysis operations.
    Infrastructure layer will provide concrete implementations
    (e.g., Google Cloud Vision, AWS Rekognition).
    """

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> ImageAnalysisResult:
        """Analyze an image and return detected labels/tags.

        Args:
            image_bytes: The image file content as bytes.

        Returns:
            ImageAnalysisResult: The analysis result with detected tags.

        Raises:
            AIServiceException: If the AI service encounters an error.
            AIServiceUnavailableException: If the AI service is unavailable.
            AIServiceRateLimitException: If rate limit is exceeded.
            NoLabelsDetectedException: If no labels are detected in the image.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the AI service is available and healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        pass


# ============================================================================
# File Validator Port
# ============================================================================


class IFileValidator(ABC):
    """Abstract interface for file validation.

    This port defines the contract for validating uploaded files.
    """

    @abstractmethod
    def validate_file(self, file_content: bytes, filename: str, content_type: str) -> None:
        """Validate an uploaded file.

        Args:
            file_content: The file content as bytes.
            filename: The original filename.
            content_type: The MIME type of the file.

        Raises:
            InvalidFileTypeException: If the file type is not allowed.
            FileTooLargeException: If the file size exceeds the limit.
            InvalidImageFormatException: If the image format is invalid.
            FileValidationException: If validation fails for other reasons.
        """
        pass

    @abstractmethod
    def get_file_extension(self, filename: str) -> str:
        """Extract and validate the file extension.

        Args:
            filename: The filename to extract extension from.

        Returns:
            str: The lowercase file extension (e.g., 'jpg', 'png').

        Raises:
            InvalidFileTypeException: If the extension is not allowed.
        """
        pass
