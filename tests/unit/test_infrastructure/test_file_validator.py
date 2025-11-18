"""Tests for FileValidator."""

from io import BytesIO
from typing import Any

import pytest
from PIL import Image

from app.core.config import Settings
from app.core.exceptions import (
    FileTooLargeException,
    InvalidFileTypeException,
    InvalidImageFormatException,
)
from app.infrastructure.validation.file_validator import FileValidator


class TestFileValidator:
    """Test suite for FileValidator."""

    @pytest.fixture
    def validator(self) -> FileValidator:
        """Create FileValidator instance."""
        return FileValidator()

    @pytest.fixture
    def valid_jpeg_bytes(self) -> bytes:
        """Create valid JPEG image bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()

    @pytest.fixture
    def valid_png_bytes(self) -> bytes:
        """Create valid PNG image bytes."""
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()

    @pytest.fixture
    def valid_webp_bytes(self) -> bytes:
        """Create valid WebP image bytes."""
        img = Image.new("RGB", (100, 100), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="WEBP")
        return img_bytes.getvalue()

    # ========================================================================
    # File Size Validation Tests
    # ========================================================================

    def test_validate_file_size_success(self, validator: FileValidator, valid_jpeg_bytes: bytes) -> None:
        """Test successful file size validation."""
        # Should not raise exception
        validator._validate_file_size(valid_jpeg_bytes, "test.jpg")

    def test_validate_file_size_too_large(self, validator: FileValidator) -> None:
        """Test file size exceeds maximum allowed."""
        # Create a file larger than 5MB
        large_file = b"x" * (6 * 1024 * 1024)  # 6MB

        with pytest.raises(FileTooLargeException) as exc_info:
            validator._validate_file_size(large_file, "large.jpg")

        assert "5 MB" in str(exc_info.value)

    def test_validate_file_size_exactly_at_limit(self, validator: FileValidator) -> None:
        """Test file size exactly at maximum allowed."""
        # Create a file exactly 5MB
        exact_size_file = b"x" * (5 * 1024 * 1024)  # 5MB

        # Should not raise exception
        validator._validate_file_size(exact_size_file, "exact.jpg")

    def test_validate_file_size_empty_file(self, validator: FileValidator) -> None:
        """Test validation of empty file."""
        empty_file = b""

        # Empty file should pass size validation (will fail format validation later)
        validator._validate_file_size(empty_file, "empty.jpg")

    # ========================================================================
    # File Extension Validation Tests
    # ========================================================================

    def test_validate_extension_jpeg(self, validator: FileValidator) -> None:
        """Test JPEG extension validation."""
        validator._validate_extension("test.jpeg")
        validator._validate_extension("test.JPEG")
        validator._validate_extension("test.jpg")
        validator._validate_extension("test.JPG")

    def test_validate_extension_png(self, validator: FileValidator) -> None:
        """Test PNG extension validation."""
        validator._validate_extension("test.png")
        validator._validate_extension("test.PNG")

    def test_validate_extension_webp(self, validator: FileValidator) -> None:
        """Test WebP extension validation."""
        validator._validate_extension("test.webp")
        validator._validate_extension("test.WEBP")

    def test_validate_extension_invalid(self, validator: FileValidator) -> None:
        """Test invalid file extension."""
        with pytest.raises(InvalidFileTypeException):
            validator._validate_extension("test.gif")

        with pytest.raises(InvalidFileTypeException):
            validator._validate_extension("test.bmp")

        with pytest.raises(InvalidFileTypeException):
            validator._validate_extension("test.txt")

        with pytest.raises(InvalidFileTypeException):
            validator._validate_extension("test.pdf")

    def test_validate_extension_no_extension(self, validator: FileValidator) -> None:
        """Test filename without extension."""
        with pytest.raises(InvalidFileTypeException):
            validator._validate_extension("no_extension")

    def test_validate_extension_multiple_dots(self, validator: FileValidator) -> None:
        """Test filename with multiple dots."""
        validator._validate_extension("my.photo.backup.jpg")

    # ========================================================================
    # Content Type Validation Tests
    # ========================================================================

    def test_validate_content_type_jpeg(self, validator: FileValidator) -> None:
        """Test JPEG content type validation."""
        validator._validate_content_type("image/jpeg")

    def test_validate_content_type_png(self, validator: FileValidator) -> None:
        """Test PNG content type validation."""
        validator._validate_content_type("image/png")

    def test_validate_content_type_webp(self, validator: FileValidator) -> None:
        """Test WebP content type validation."""
        validator._validate_content_type("image/webp")

    def test_validate_content_type_invalid(self, validator: FileValidator) -> None:
        """Test invalid content type."""
        with pytest.raises(InvalidFileTypeException):
            validator._validate_content_type("image/gif")

        with pytest.raises(InvalidFileTypeException):
            validator._validate_content_type("application/pdf")

        with pytest.raises(InvalidFileTypeException):
            validator._validate_content_type("text/plain")

    def test_validate_content_type_case_insensitive(self, validator: FileValidator) -> None:
        """Test content type validation is case-insensitive."""
        validator._validate_content_type("IMAGE/JPEG")
        validator._validate_content_type("Image/Png")

    # ========================================================================
    # Image Format Validation Tests
    # ========================================================================

    def test_validate_image_format_jpeg(self, validator: FileValidator, valid_jpeg_bytes: bytes) -> None:
        """Test valid JPEG image format."""
        validator._validate_image_format(valid_jpeg_bytes)

    def test_validate_image_format_png(self, validator: FileValidator, valid_png_bytes: bytes) -> None:
        """Test valid PNG image format."""
        validator._validate_image_format(valid_png_bytes)

    def test_validate_image_format_webp(self, validator: FileValidator, valid_webp_bytes: bytes) -> None:
        """Test valid WebP image format."""
        validator._validate_image_format(valid_webp_bytes)

    def test_validate_image_format_corrupted(self, validator: FileValidator) -> None:
        """Test corrupted image data."""
        corrupted_data = b"This is not an image"

        with pytest.raises(InvalidImageFormatException):
            validator._validate_image_format(corrupted_data)

    def test_validate_image_format_empty(self, validator: FileValidator) -> None:
        """Test empty image data."""
        with pytest.raises(InvalidImageFormatException):
            validator._validate_image_format(b"")

    def test_validate_image_format_partial_data(self, validator: FileValidator) -> None:
        """Test partial/truncated image data."""
        partial_data = b"\xff\xd8\xff\xe0"  # JPEG header only

        with pytest.raises(InvalidImageFormatException):
            validator._validate_image_format(partial_data)

    # ========================================================================
    # Full Validation Tests
    # ========================================================================

    def test_validate_file_success_jpeg(
        self, validator: FileValidator, valid_jpeg_bytes: bytes
    ) -> None:
        """Test complete validation of valid JPEG file."""
        # Should not raise exception
        validator.validate_file(valid_jpeg_bytes, "test.jpg", "image/jpeg")

    def test_validate_file_success_png(
        self, validator: FileValidator, valid_png_bytes: bytes
    ) -> None:
        """Test complete validation of valid PNG file."""
        validator.validate_file(valid_png_bytes, "test.png", "image/png")

    def test_validate_file_success_webp(
        self, validator: FileValidator, valid_webp_bytes: bytes
    ) -> None:
        """Test complete validation of valid WebP file."""
        validator.validate_file(valid_webp_bytes, "test.webp", "image/webp")

    def test_validate_file_size_exceeds(
        self, validator: FileValidator
    ) -> None:
        """Test validation fails when file is too large."""
        large_file = b"x" * (6 * 1024 * 1024)  # 6MB

        with pytest.raises(FileTooLargeException):
            validator.validate_file(large_file, "large.jpg", "image/jpeg")

    def test_validate_file_wrong_extension(
        self, validator: FileValidator, valid_jpeg_bytes: bytes
    ) -> None:
        """Test validation fails with wrong extension."""
        with pytest.raises(InvalidFileTypeException):
            validator.validate_file(valid_jpeg_bytes, "test.gif", "image/jpeg")

    def test_validate_file_wrong_content_type(
        self, validator: FileValidator, valid_jpeg_bytes: bytes
    ) -> None:
        """Test validation fails with wrong content type."""
        with pytest.raises(InvalidFileTypeException):
            validator.validate_file(valid_jpeg_bytes, "test.jpg", "text/plain")

    def test_validate_file_extension_content_type_mismatch(
        self, validator: FileValidator, valid_jpeg_bytes: bytes
    ) -> None:
        """Test validation with mismatched extension and content type."""
        # Extension says PNG but content type says JPEG
        # Both are valid types, so should pass initial checks
        # But actual image format validation will determine if it's really valid
        validator.validate_file(valid_jpeg_bytes, "test.png", "image/jpeg")

    def test_validate_file_corrupted_with_valid_metadata(
        self, validator: FileValidator
    ) -> None:
        """Test validation fails when file is corrupted despite valid metadata."""
        corrupted_data = b"Not a real image"

        with pytest.raises(InvalidImageFormatException):
            validator.validate_file(corrupted_data, "test.jpg", "image/jpeg")

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_validate_very_small_image(self, validator: FileValidator) -> None:
        """Test validation of very small (1x1 pixel) image."""
        tiny_img = Image.new("RGB", (1, 1), color="white")
        img_bytes = BytesIO()
        tiny_img.save(img_bytes, format="JPEG")
        tiny_bytes = img_bytes.getvalue()

        validator.validate_file(tiny_bytes, "tiny.jpg", "image/jpeg")

    def test_validate_large_valid_image(self, validator: FileValidator) -> None:
        """Test validation of large but valid image (under 5MB)."""
        # Create a large image but compress it to stay under 5MB
        large_img = Image.new("RGB", (2000, 2000), color="red")
        img_bytes = BytesIO()
        large_img.save(img_bytes, format="JPEG", quality=50)  # Lower quality to reduce size
        large_bytes = img_bytes.getvalue()

        # Only test if it's actually under 5MB
        if len(large_bytes) < 5 * 1024 * 1024:
            validator.validate_file(large_bytes, "large.jpg", "image/jpeg")

    def test_validate_file_with_unicode_filename(
        self, validator: FileValidator, valid_jpeg_bytes: bytes
    ) -> None:
        """Test validation with Unicode characters in filename."""
        validator.validate_file(valid_jpeg_bytes, "фото.jpg", "image/jpeg")
        validator.validate_file(valid_jpeg_bytes, "画像.jpg", "image/jpeg")
        validator.validate_file(valid_jpeg_bytes, "صورة.jpg", "image/jpeg")