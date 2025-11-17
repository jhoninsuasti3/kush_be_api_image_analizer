"""Google Cloud Vision API implementation of IAIService.

This module provides image analysis functionality using Google Cloud Vision API.
"""

import os

from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, ServiceUnavailable
from google.cloud import vision
from google.oauth2 import service_account

from app.core.config import settings
from app.core.exceptions import (
    AIServiceException,
    AIServiceRateLimitException,
    AIServiceUnavailableException,
    NoLabelsDetectedException,
)
from app.core.logging import get_logger
from app.domain.models import ImageAnalysisResult, Tag
from app.domain.ports import IAIService

logger = get_logger(__name__)


class GoogleVisionService(IAIService):
    """Google Cloud Vision API implementation for image analysis.

    This class uses Google Cloud Vision's label detection to analyze images
    and return tags with confidence scores.
    """

    def __init__(self) -> None:
        """Initialize the Google Vision client.

        The client uses credentials from GOOGLE_APPLICATION_CREDENTIALS
        environment variable or from settings.
        """
        try:
            # Get credentials path from settings or environment
            credentials_path = settings.google_application_credentials or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

            if credentials_path and os.path.exists(credentials_path):
                # Load credentials from file explicitly
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info("google_vision_client_initialized", credentials_path=credentials_path)
            else:
                # Fallback to default credentials
                self.client = vision.ImageAnnotatorClient()
                logger.info("google_vision_client_initialized", credentials="default")
        except Exception as e:
            logger.error("google_vision_client_init_failed", error=str(e))
            raise AIServiceException(f"Failed to initialize Google Vision client: {e}") from e

    async def analyze_image(self, image_bytes: bytes) -> ImageAnalysisResult:
        """Analyze an image using Google Cloud Vision API.

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
        try:
            logger.info(
                "analyzing_image_with_google_vision",
                image_size_kb=len(image_bytes) / 1024,
            )

            # Create Vision API image object
            image = vision.Image(content=image_bytes)

            # Perform label detection
            response = self.client.label_detection(image=image)

            # Check for errors in response
            if response.error.message:
                logger.error(
                    "google_vision_error_response",
                    error=response.error.message,
                )
                raise AIServiceException(f"Google Vision API error: {response.error.message}")

            # Extract labels
            labels = response.label_annotations

            if not labels:
                logger.warning("no_labels_detected")
                raise NoLabelsDetectedException("No labels detected in the image")

            # Convert Google Vision labels to our Tag model
            tags = [
                Tag(
                    label=label.description,
                    confidence=label.score,  # Google returns score as 0-1 float
                )
                for label in labels
            ]

            logger.info(
                "image_analyzed_successfully",
                tags_count=len(tags),
                top_tag=tags[0].label if tags else None,
                top_confidence=tags[0].confidence if tags else None,
            )

            return ImageAnalysisResult(tags=tags)

        except NoLabelsDetectedException:
            raise

        except ResourceExhausted as e:
            logger.error("google_vision_rate_limit", error=str(e))
            raise AIServiceRateLimitException("Google Vision API rate limit exceeded. Please try again later.") from e

        except ServiceUnavailable as e:
            logger.error("google_vision_unavailable", error=str(e))
            raise AIServiceUnavailableException(
                "Google Vision API is currently unavailable. Please try again later."
            ) from e

        except GoogleAPIError as e:
            logger.error("google_vision_api_error", error=str(e))
            raise AIServiceException(f"Google Vision API error: {e}") from e

        except Exception as e:
            logger.error("image_analysis_failed", error=str(e))
            raise AIServiceException(f"Failed to analyze image: {e}") from e

    async def health_check(self) -> bool:
        """Check if Google Vision API is available and healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        try:
            # Try a minimal operation to check connectivity
            # We'll use a 1x1 pixel image as a test
            test_image_bytes = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
                b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
                b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            )

            image = vision.Image(content=test_image_bytes)
            response = self.client.label_detection(image=image)

            # If we get here without exception, service is healthy
            logger.debug("google_vision_health_check_passed")
            return not bool(response.error.message)

        except Exception as e:
            logger.warning("google_vision_health_check_failed", error=str(e))
            return False
