"""Service dependencies for FastAPI.

Provides dependency injection for application services.
"""

from fastapi import Depends

from app.application.services.image_analysis_service import ImageAnalysisService
from app.infrastructure.ai.google_vision_service import GoogleVisionService
from app.infrastructure.validation.file_validator import FileValidator


def get_file_validator() -> FileValidator:
    """Get file validator instance.

    Returns:
        FileValidator: File validator instance.
    """
    return FileValidator()


def get_ai_service() -> GoogleVisionService:
    """Get AI service instance.

    Returns:
        GoogleVisionService: Google Vision AI service instance.
    """
    return GoogleVisionService()


def get_image_analysis_service(
    ai_service: GoogleVisionService = Depends(get_ai_service),
    file_validator: FileValidator = Depends(get_file_validator),
) -> ImageAnalysisService:
    """Get image analysis service instance.

    Args:
        ai_service: Injected AI service.
        file_validator: Injected file validator.

    Returns:
        ImageAnalysisService: Image analysis service instance.
    """
    return ImageAnalysisService(
        ai_service=ai_service,
        file_validator=file_validator,
    )
