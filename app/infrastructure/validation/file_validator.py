"""File validator implementation for image uploads.

This module provides file validation functionality including:
- File size validation
- File type/extension validation
- Image format validation using Pillow
"""

import io
from pathlib import Path

from PIL import Image

from app.core.config import settings
from app.core.exceptions import FileTooLargeException, InvalidFileTypeException, InvalidImageFormatException
from app.core.logging import get_logger
from app.domain.ports import IFileValidator

logger = get_logger(__name__)


class FileValidator(IFileValidator):
    """File validator implementation.

    Validates uploaded files for size, type, and format before processing.
    """

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
        logger.debug(
            "validating_file",
            filename=filename,
            content_type=content_type,
            size_bytes=len(file_content),
        )

        # 1. Validate file size
        self._validate_file_size(file_content, filename)

        # 2. Validate file extension
        extension = self.get_file_extension(filename)
        self._validate_extension(extension, filename)

        # 3. Validate content type
        self._validate_content_type(content_type, filename)

        # 4. Validate image format (try to open with Pillow)
        self._validate_image_format(file_content, filename)

        logger.info(
            "file_validated",
            filename=filename,
            extension=extension,
            size_kb=len(file_content) / 1024,
        )

    def get_file_extension(self, filename: str) -> str:
        """Extract and validate the file extension.

        Args:
            filename: The filename to extract extension from.

        Returns:
            str: The lowercase file extension (e.g., 'jpg', 'png').

        Raises:
            InvalidFileTypeException: If the extension is not allowed.
        """
        path = Path(filename)
        extension = path.suffix.lstrip(".").lower()

        if not extension:
            logger.warning("file_no_extension", filename=filename)
            raise InvalidFileTypeException("File must have an extension")

        if extension not in settings.allowed_extensions_list:
            logger.warning(
                "file_extension_not_allowed",
                filename=filename,
                extension=extension,
                allowed=settings.allowed_extensions_list,
            )
            raise InvalidFileTypeException(
                f"File extension '.{extension}' not allowed. "
                f"Allowed extensions: {', '.join(settings.allowed_extensions_list)}"
            )

        return extension

    def _validate_file_size(self, file_content: bytes, filename: str) -> None:
        """Validate file size against maximum limit.

        Args:
            file_content: The file content as bytes.
            filename: The filename for logging.

        Raises:
            FileTooLargeException: If the file size exceeds the limit.
        """
        file_size = len(file_content)
        max_size = settings.max_file_size_bytes

        if file_size > max_size:
            logger.warning(
                "file_too_large",
                filename=filename,
                size_mb=file_size / 1024 / 1024,
                max_size_mb=settings.max_file_size_mb,
            )
            raise FileTooLargeException(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({settings.max_file_size_mb} MB)"
            )

    def _validate_extension(self, extension: str, filename: str | None = None) -> None:
        """Validate file extension.

        Args:
            extension: The file extension (without dot).
            filename: The filename for logging.

        Raises:
            InvalidFileTypeException: If the extension is not allowed.
        """
        if filename is None:
            filename = extension
            extension = Path(extension).suffix.lstrip(".").lower()

        if extension not in settings.allowed_extensions_list:
            logger.warning(
                "invalid_file_extension",
                filename=filename,
                extension=extension,
            )
            raise InvalidFileTypeException(
                f"File extension '.{extension}' not allowed. Allowed: {', '.join(settings.allowed_extensions_list)}"
            )

    def _validate_content_type(self, content_type: str, filename: str | None = None) -> None:
        """Validate MIME content type.

        Args:
            content_type: The MIME type (e.g., 'image/jpeg').
            filename: The filename for logging.

        Raises:
            InvalidFileTypeException: If the content type is not an allowed image type.
        """
        # Allowed MIME types based on allowed extensions
        allowed_mime_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        }

        if content_type.lower() not in allowed_mime_types:
            logger.warning(
                "invalid_content_type",
                filename=filename or "uploaded_file",
                content_type=content_type,
            )
            raise InvalidFileTypeException(
                f"Content type '{content_type}' is not allowed. "
                f"Allowed types: {', '.join(sorted(allowed_mime_types))}"
            )

    def _validate_image_format(self, file_content: bytes, filename: str | None = None) -> None:
        """Validate that the file is a valid image using Pillow.

        Args:
            file_content: The file content as bytes.
            filename: The filename for logging.

        Raises:
            InvalidImageFormatException: If the image format is invalid or corrupted.
        """
        try:
            # Try to open the image with Pillow
            image = Image.open(io.BytesIO(file_content))

            # Verify the image by loading it
            image.verify()

            logger.debug(
                "image_format_validated",
                filename=filename or "uploaded_file",
                format=image.format,
                size=image.size,
                mode=image.mode,
            )

        except Exception as e:
            logger.error(
                "invalid_image_format",
                filename=filename or "uploaded_file",
                error=str(e),
            )
            raise InvalidImageFormatException(f"Invalid or corrupted image file: {e}") from e
