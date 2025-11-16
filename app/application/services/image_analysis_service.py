"""Image analysis service for processing and analyzing images.

This module orchestrates image validation and AI analysis.
"""

from app.core.logging import get_logger
from app.domain.models import ImageAnalysisRequest, ImageAnalysisResult
from app.domain.ports import IAIService, IFileValidator

logger = get_logger(__name__)


class ImageAnalysisService:
    """Image analysis service.

    Coordinates file validation and AI-powered image analysis.
    """

    def __init__(self, ai_service: IAIService, file_validator: IFileValidator) -> None:
        """Initialize the image analysis service.

        Args:
            ai_service: AI service for image analysis.
            file_validator: Validator for uploaded files.
        """
        self.ai_service = ai_service
        self.file_validator = file_validator

    async def analyze_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_email: str,
    ) -> ImageAnalysisResult:
        """Analyze an uploaded image.

        Args:
            file_content: The image file content as bytes.
            filename: The original filename.
            content_type: The MIME type of the file.
            user_email: Email of the user requesting the analysis.

        Returns:
            ImageAnalysisResult: The analysis result with detected tags.

        Raises:
            FileValidationException: If file validation fails.
            AIServiceException: If image analysis fails.
        """
        logger.info(
            "image_analysis_started",
            user_email=user_email,
            filename=filename,
            size_kb=len(file_content) / 1024,
        )

        # Create analysis request for logging
        request = ImageAnalysisRequest(
            user_email=user_email,
            file_name=filename,
            file_size=len(file_content),
            content_type=content_type,
        )

        logger.debug(
            "analysis_request_details",
            request_data=request.model_dump(),
        )

        # Step 1: Validate the file
        self.file_validator.validate_file(file_content, filename, content_type)
        logger.info("file_validation_passed", filename=filename)

        # Step 2: Analyze the image with AI
        result = await self.ai_service.analyze_image(file_content)

        logger.info(
            "image_analysis_completed",
            user_email=user_email,
            filename=filename,
            tags_count=len(result.tags),
        )

        return result
