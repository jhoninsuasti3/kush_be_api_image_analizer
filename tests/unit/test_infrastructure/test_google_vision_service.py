"""Tests for GoogleVisionService."""

from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, ServiceUnavailable
from PIL import Image

from app.core.exceptions import (
    AIServiceException,
    AIServiceRateLimitException,
    AIServiceUnavailableException,
    NoLabelsDetectedException,
)
from app.domain.models import ImageAnalysisResult
from app.infrastructure.ai.google_vision_service import GoogleVisionService


class TestGoogleVisionService:
    """Test suite for GoogleVisionService."""

    @pytest.fixture
    def test_image_bytes(self) -> bytes:
        """Create test image bytes."""
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        return img_bytes.getvalue()

    @pytest.fixture
    def mock_vision_client(self) -> MagicMock:
        """Create mocked Vision client."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_vision_client: MagicMock) -> GoogleVisionService:
        """Create GoogleVisionService with mocked client."""
        with patch("app.infrastructure.ai.google_vision_service.vision.ImageAnnotatorClient") as mock_client_class:
            mock_client_class.return_value = mock_vision_client
            service = GoogleVisionService()
            service.client = mock_vision_client
            return service

    # ========================================================================
    # Initialization Tests
    # ========================================================================

    def test_service_initialization(self) -> None:
        """Test service initializes correctly."""
        with patch("app.infrastructure.ai.google_vision_service.vision.ImageAnnotatorClient"):
            service = GoogleVisionService()
            assert service.client is not None

    # ========================================================================
    # Successful Analysis Tests
    # ========================================================================

    def test_analyze_image_success_single_label(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test successful image analysis with single label."""
        # Mock response
        mock_label = Mock()
        mock_label.description = "Cat"
        mock_label.score = 0.95

        mock_response = Mock()
        mock_response.label_annotations = [mock_label]
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        # Analyze image
        result = service.analyze_image(test_image_bytes)

        assert isinstance(result, ImageAnalysisResult)
        assert len(result.tags) == 1
        assert result.tags[0].label == "Cat"
        assert result.tags[0].confidence == 0.95

    def test_analyze_image_success_multiple_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test successful image analysis with multiple labels."""
        # Mock response with multiple labels
        mock_labels = [
            Mock(description="Cat", score=0.95),
            Mock(description="Animal", score=0.92),
            Mock(description="Pet", score=0.88),
            Mock(description="Mammal", score=0.85),
        ]

        mock_response = Mock()
        mock_response.label_annotations = mock_labels
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        # Analyze image
        result = service.analyze_image(test_image_bytes)

        assert len(result.tags) == 4
        assert result.tags[0].label == "Cat"
        assert result.tags[0].confidence == 0.95
        assert result.tags[3].label == "Mammal"
        assert result.tags[3].confidence == 0.85

    def test_analyze_image_labels_sorted_by_confidence(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test that labels are sorted by confidence score."""
        # Mock response with unsorted labels
        mock_labels = [
            Mock(description="Low", score=0.50),
            Mock(description="High", score=0.95),
            Mock(description="Medium", score=0.75),
        ]

        mock_response = Mock()
        mock_response.label_annotations = mock_labels
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        # Analyze image
        result = service.analyze_image(test_image_bytes)

        # Should be sorted by confidence (highest first)
        assert result.tags[0].confidence >= result.tags[1].confidence
        assert result.tags[1].confidence >= result.tags[2].confidence

    # ========================================================================
    # No Labels Detected Tests
    # ========================================================================

    def test_analyze_image_no_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test image analysis when no labels are detected."""
        mock_response = Mock()
        mock_response.label_annotations = []
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        with pytest.raises(NoLabelsDetectedException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "no labels" in str(exc_info.value).lower()

    def test_analyze_image_none_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test image analysis when labels are None."""
        mock_response = Mock()
        mock_response.label_annotations = None
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        with pytest.raises(NoLabelsDetectedException):
            service.analyze_image(test_image_bytes)

    # ========================================================================
    # Error Response Tests
    # ========================================================================

    def test_analyze_image_api_error_response(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test handling of API error in response."""
        mock_response = Mock()
        mock_response.label_annotations = []
        mock_response.error.message = "Invalid image format"

        mock_vision_client.label_detection.return_value = mock_response

        with pytest.raises(AIServiceException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "invalid image format" in str(exc_info.value).lower()

    # ========================================================================
    # Exception Handling Tests
    # ========================================================================

    def test_analyze_image_rate_limit_exception(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test handling of rate limit exception."""
        mock_vision_client.label_detection.side_effect = ResourceExhausted("Rate limit exceeded")

        with pytest.raises(AIServiceRateLimitException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "rate limit" in str(exc_info.value).lower()

    def test_analyze_image_service_unavailable_exception(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test handling of service unavailable exception."""
        mock_vision_client.label_detection.side_effect = ServiceUnavailable("Service is down")

        with pytest.raises(AIServiceUnavailableException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "unavailable" in str(exc_info.value).lower()

    def test_analyze_image_generic_google_api_error(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test handling of generic Google API error."""
        mock_vision_client.label_detection.side_effect = GoogleAPIError("Something went wrong")

        with pytest.raises(AIServiceException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "google vision api error" in str(exc_info.value).lower()

    def test_analyze_image_unexpected_exception(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test handling of unexpected exception."""
        mock_vision_client.label_detection.side_effect = ValueError("Unexpected error")

        with pytest.raises(AIServiceException) as exc_info:
            service.analyze_image(test_image_bytes)

        assert "unexpected error" in str(exc_info.value).lower()

    # ========================================================================
    # Health Check Tests
    # ========================================================================

    def test_health_check_success(self, service: GoogleVisionService, mock_vision_client: MagicMock) -> None:
        """Test successful health check."""
        # Mock successful label detection
        mock_response = Mock()
        mock_response.label_annotations = [Mock(description="Test", score=0.9)]
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        assert service.health_check() is True

    def test_health_check_failure(self, service: GoogleVisionService, mock_vision_client: MagicMock) -> None:
        """Test health check failure."""
        mock_vision_client.label_detection.side_effect = GoogleAPIError("Service error")

        assert service.health_check() is False

    def test_health_check_service_unavailable(
        self, service: GoogleVisionService, mock_vision_client: MagicMock
    ) -> None:
        """Test health check when service is unavailable."""
        mock_vision_client.label_detection.side_effect = ServiceUnavailable("Service down")

        assert service.health_check() is False

    def test_health_check_uses_test_image(self, service: GoogleVisionService, mock_vision_client: MagicMock) -> None:
        """Test that health check uses a test image."""
        mock_response = Mock()
        mock_response.label_annotations = [Mock(description="Test", score=0.9)]
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        service.health_check()

        # Verify label_detection was called
        mock_vision_client.label_detection.assert_called_once()

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_analyze_image_with_low_confidence_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test analysis with low confidence labels."""
        mock_labels = [
            Mock(description="Uncertain", score=0.15),
            Mock(description="Maybe", score=0.10),
        ]

        mock_response = Mock()
        mock_response.label_annotations = mock_labels
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        result = service.analyze_image(test_image_bytes)

        # Should still return results even with low confidence
        assert len(result.tags) == 2
        assert all(tag.confidence < 0.5 for tag in result.tags)

    def test_analyze_image_with_special_characters_in_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test analysis with special characters in label descriptions."""
        mock_labels = [
            Mock(description="Café", score=0.90),
            Mock(description="日本語", score=0.85),
            Mock(description="Ñoño", score=0.80),
        ]

        mock_response = Mock()
        mock_response.label_annotations = mock_labels
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        result = service.analyze_image(test_image_bytes)

        assert len(result.tags) == 3
        assert result.tags[0].label == "Café"
        assert result.tags[1].label == "日本語"

    def test_analyze_image_empty_bytes(self, service: GoogleVisionService, mock_vision_client: MagicMock) -> None:
        """Test analysis with empty image bytes."""
        mock_vision_client.label_detection.side_effect = GoogleAPIError("Invalid image")

        with pytest.raises(AIServiceException):
            service.analyze_image(b"")

    def test_analyze_image_very_large_number_of_labels(
        self, service: GoogleVisionService, test_image_bytes: bytes, mock_vision_client: MagicMock
    ) -> None:
        """Test analysis with many labels returned."""
        # Create 50 mock labels
        mock_labels = [Mock(description=f"Label{i}", score=0.95 - (i * 0.01)) for i in range(50)]

        mock_response = Mock()
        mock_response.label_annotations = mock_labels
        mock_response.error.message = ""

        mock_vision_client.label_detection.return_value = mock_response

        result = service.analyze_image(test_image_bytes)

        assert len(result.tags) == 50
        # Verify first and last labels
        assert result.tags[0].label in [label.description for label in mock_labels]
