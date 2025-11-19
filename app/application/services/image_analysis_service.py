"""Image analysis service for processing and analyzing images.

This module orchestrates file validation, AI analysis, and persistence.
"""

import uuid
from datetime import datetime

from app.core.logging import get_logger
from app.domain.models import ImageAnalysis, ImageAnalysisRequest, ImageAnalysisResult
from app.domain.ports import IAIService, IFileValidator, IImageAnalysisRepository

logger = get_logger(__name__)


class ImageAnalysisService:
    """Image analysis service.

    Coordinates file validation, AI-powered image analysis, and persistence.
    """

    def __init__(
        self,
        ai_service: IAIService,
        file_validator: IFileValidator,
        analysis_repository: IImageAnalysisRepository | None = None,
    ) -> None:
        """Initialize the image analysis service.

        Args:
            ai_service: AI service for image analysis.
            file_validator: Validator for uploaded files.
            analysis_repository: Repository for persisting analysis records (optional).
        """
        self.ai_service = ai_service
        self.file_validator = file_validator
        self.analysis_repository = analysis_repository

    def analyze_image(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_email: str | None = None,
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
        user_identifier = user_email or "anonymous"

        logger.info(
            "image_analysis_started",
            user_email=user_identifier,
            filename=filename,
            size_kb=len(file_content) / 1024,
        )

        # Create analysis request for logging
        request = ImageAnalysisRequest(
            user_email=user_identifier,
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
        result = self.ai_service.analyze_image(file_content)

        logger.info(
            "image_analysis_completed",
            user_email=user_identifier,
            filename=filename,
            tags_count=len(result.tags),
        )

        # Step 3: Persist the analysis record (if repository is configured)
        if self.analysis_repository and user_email:
            try:
                analysis_record = ImageAnalysis(
                    analysis_id=str(uuid.uuid4()),
                    user_email=user_email,
                    file_name=filename,
                    file_size=len(file_content),
                    content_type=content_type,
                    tags=result.tags,
                    analyzed_at=datetime.utcnow(),
                )
                self.analysis_repository.create(analysis_record)
                logger.info(
                    "analysis_record_persisted",
                    analysis_id=analysis_record.analysis_id,
                    user_email=user_email,
                )
            except Exception as e:
                # Log error but don't fail the analysis
                # This ensures analysis still works even if persistence fails
                logger.error(
                    "analysis_persistence_failed",
                    user_email=user_email,
                    filename=filename,
                    error=str(e),
                )

        return result
