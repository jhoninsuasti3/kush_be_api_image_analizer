"""Tests for ImageAnalysisService."""

from io import BytesIO
from unittest.mock import Mock

import pytest
from PIL import Image

from app.application.services.image_analysis_service import ImageAnalysisService
from app.core.exceptions import (
    AIServiceException,
    FileTooLargeException,
    InvalidFileTypeException,
    InvalidImageFormatException,
)
from app.domain.models import ImageAnalysisResult, Tag
from app.domain.ports import IAIService, IFileValidator


class TestImageAnalysisService:
    """Test suite for ImageAnalysisService."""

    @pytest.fixture
    def mock_file_validator(self) -> Mock:
        """Create mock file validator."""
        return Mock(spec=IFileValidator)

    @pytest.fixture
    def mock_ai_service(self) -> Mock:
        """Create mock AI service."""
        return Mock(spec=IAIService)

    @pytest.fixture
    def image_analysis_service(
        self, mock_file_validator: Mock, mock_ai_service: Mock
    ) -> ImageAnalysisService:
        """Create ImageAnalysisService with mocked dependencies."""
        return ImageAnalysisService(
            file_validator=mock_file_validator,
            ai_service=mock_ai_service,
        )

    @pytest.fixture
    def valid_image_bytes(self) -> bytes:
        """Create valid image bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()

    @pytest.fixture
    def sample_analysis_result(self) -> ImageAnalysisResult:
        """Create sample analysis result."""
        return ImageAnalysisResult(
            tags=[
                Tag(label="Cat", confidence=0.95),
                Tag(label="Animal", confidence=0.90),
                Tag(label="Pet", confidence=0.85),
            ]
        )

    # ========================================================================
    # Successful Analysis Tests
    # ========================================================================

    def test_analyze_image_success(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test successful image analysis."""
        filename = "test.jpg"
        content_type = "image/jpeg"

        # Mock validator (no exception = valid)
        mock_file_validator.validate_file.return_value = None

        # Mock AI service
        mock_ai_service.analyze_image.return_value = sample_analysis_result

        # Analyze image
        result = image_analysis_service.analyze_image(valid_image_bytes, filename, content_type)

        # Verify
        assert result == sample_analysis_result
        assert len(result.tags) == 3
        assert result.tags[0].label == "Cat"

        # Verify calls
        mock_file_validator.validate_file.assert_called_once_with(
            valid_image_bytes, filename, content_type
        )
        mock_ai_service.analyze_image.assert_called_once_with(valid_image_bytes)

    def test_analyze_image_multiple_tags(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test image analysis with multiple tags."""
        result_with_many_tags = ImageAnalysisResult(
            tags=[
                Tag(label="Dog", confidence=0.98),
                Tag(label="Golden Retriever", confidence=0.95),
                Tag(label="Animal", confidence=0.93),
                Tag(label="Pet", confidence=0.90),
                Tag(label="Mammal", confidence=0.88),
            ]
        )

        mock_ai_service.analyze_image.return_value = result_with_many_tags

        result = image_analysis_service.analyze_image(
            valid_image_bytes, "dog.jpg", "image/jpeg"
        )

        assert len(result.tags) == 5
        assert result.tags[0].confidence > result.tags[-1].confidence

    # ========================================================================
    # Validation Error Tests
    # ========================================================================

    def test_analyze_image_file_too_large(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis fails when file is too large."""
        mock_file_validator.validate_file.side_effect = FileTooLargeException(
            "File size exceeds 5 MB limit"
        )

        with pytest.raises(FileTooLargeException) as exc_info:
            image_analysis_service.analyze_image(valid_image_bytes, "large.jpg", "image/jpeg")

        assert "5 MB" in str(exc_info.value)

        # AI service should not be called
        mock_ai_service.analyze_image.assert_not_called()

    def test_analyze_image_invalid_file_type(
        self,
        image_analysis_service: ImageAnalysisService,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis fails with invalid file type."""
        invalid_file = b"This is a text file"

        mock_file_validator.validate_file.side_effect = InvalidFileTypeException(
            "Invalid file type"
        )

        with pytest.raises(InvalidFileTypeException):
            image_analysis_service.analyze_image(invalid_file, "file.txt", "text/plain")

        mock_ai_service.analyze_image.assert_not_called()

    def test_analyze_image_invalid_image_format(
        self,
        image_analysis_service: ImageAnalysisService,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis fails with invalid image format."""
        corrupted_image = b"Not a valid image"

        mock_file_validator.validate_file.side_effect = InvalidImageFormatException(
            "Invalid image format"
        )

        with pytest.raises(InvalidImageFormatException):
            image_analysis_service.analyze_image(
                corrupted_image, "corrupted.jpg", "image/jpeg"
            )

        mock_ai_service.analyze_image.assert_not_called()

    # ========================================================================
    # AI Service Error Tests
    # ========================================================================

    def test_analyze_image_ai_service_error(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis fails when AI service raises error."""
        mock_ai_service.analyze_image.side_effect = AIServiceException(
            "AI service error"
        )

        with pytest.raises(AIServiceException) as exc_info:
            image_analysis_service.analyze_image(
                valid_image_bytes, "test.jpg", "image/jpeg"
            )

        assert "AI service error" in str(exc_info.value)

        # Validator should have been called
        mock_file_validator.validate_file.assert_called_once()

    # ========================================================================
    # Service Orchestration Tests
    # ========================================================================

    def test_analyze_image_calls_validator_before_ai(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test that file validator is called before AI service."""
        call_order = []

        def validator_side_effect(*args, **kwargs):  # type: ignore
            call_order.append("validator")

        def ai_service_side_effect(*args, **kwargs):  # type: ignore
            call_order.append("ai_service")
            return sample_analysis_result

        mock_file_validator.validate_file.side_effect = validator_side_effect
        mock_ai_service.analyze_image.side_effect = ai_service_side_effect

        image_analysis_service.analyze_image(
            valid_image_bytes, "test.jpg", "image/jpeg"
        )

        # Validator should be called first
        assert call_order == ["validator", "ai_service"]

    def test_analyze_image_passes_correct_parameters(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test that correct parameters are passed to dependencies."""
        filename = "my_photo.jpeg"
        content_type = "image/jpeg"

        mock_ai_service.analyze_image.return_value = sample_analysis_result

        image_analysis_service.analyze_image(valid_image_bytes, filename, content_type)

        # Verify validator received correct params
        validator_call_args = mock_file_validator.validate_file.call_args
        assert validator_call_args[0][0] == valid_image_bytes
        assert validator_call_args[0][1] == filename
        assert validator_call_args[0][2] == content_type

        # Verify AI service received correct params
        ai_call_args = mock_ai_service.analyze_image.call_args
        assert ai_call_args[0][0] == valid_image_bytes

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_analyze_image_with_png(
        self,
        image_analysis_service: ImageAnalysisService,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis with PNG image."""
        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        png_bytes = img_bytes.getvalue()

        mock_ai_service.analyze_image.return_value = sample_analysis_result

        result = image_analysis_service.analyze_image(png_bytes, "test.png", "image/png")

        assert result == sample_analysis_result
        mock_file_validator.validate_file.assert_called_once_with(
            png_bytes, "test.png", "image/png"
        )

    def test_analyze_image_with_webp(
        self,
        image_analysis_service: ImageAnalysisService,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis with WebP image."""
        img = Image.new("RGB", (100, 100), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="WEBP")
        webp_bytes = img_bytes.getvalue()

        mock_ai_service.analyze_image.return_value = sample_analysis_result

        result = image_analysis_service.analyze_image(
            webp_bytes, "test.webp", "image/webp"
        )

        assert result == sample_analysis_result

    def test_analyze_image_empty_result_tags(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis with empty tags result."""
        empty_result = ImageAnalysisResult(tags=[])

        mock_ai_service.analyze_image.return_value = empty_result

        result = image_analysis_service.analyze_image(
            valid_image_bytes, "test.jpg", "image/jpeg"
        )

        assert len(result.tags) == 0

    def test_analyze_image_with_unicode_filename(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        sample_analysis_result: ImageAnalysisResult,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis with Unicode filename."""
        unicode_filename = "фото_日本語_صورة.jpg"

        mock_ai_service.analyze_image.return_value = sample_analysis_result

        result = image_analysis_service.analyze_image(
            valid_image_bytes, unicode_filename, "image/jpeg"
        )

        assert result == sample_analysis_result
        mock_file_validator.validate_file.assert_called_once_with(
            valid_image_bytes, unicode_filename, "image/jpeg"
        )

    def test_analyze_image_single_tag_result(
        self,
        image_analysis_service: ImageAnalysisService,
        valid_image_bytes: bytes,
        mock_file_validator: Mock,
        mock_ai_service: Mock,
    ) -> None:
        """Test analysis returning single tag."""
        single_tag_result = ImageAnalysisResult(
            tags=[Tag(label="Cat", confidence=0.99)]
        )

        mock_ai_service.analyze_image.return_value = single_tag_result

        result = image_analysis_service.analyze_image(
            valid_image_bytes, "cat.jpg", "image/jpeg"
        )

        assert len(result.tags) == 1
        assert result.tags[0].label == "Cat"
        assert result.tags[0].confidence == 0.99