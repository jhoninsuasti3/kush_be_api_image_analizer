"""Service dependencies for FastAPI.

Provides dependency injection for application services.
"""

from fastapi import Depends

from app.application.services.image_analysis_service import ImageAnalysisService
from app.infrastructure.ai.google_vision_service import GoogleVisionService
from app.infrastructure.persistence.image_analysis_repository import DynamoDBImageAnalysisRepository
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


def get_analysis_repository() -> DynamoDBImageAnalysisRepository:
    """Get image analysis repository instance.

    Returns:
        DynamoDBImageAnalysisRepository: DynamoDB analysis repository instance.
    """
    return DynamoDBImageAnalysisRepository()


def get_image_analysis_service(
    ai_service: GoogleVisionService = Depends(get_ai_service),
    file_validator: FileValidator = Depends(get_file_validator),
    analysis_repository: DynamoDBImageAnalysisRepository = Depends(get_analysis_repository),
) -> ImageAnalysisService:
    """Get image analysis service instance.

    Args:
        ai_service: Injected AI service.
        file_validator: Injected file validator.
        analysis_repository: Injected analysis repository.

    Returns:
        ImageAnalysisService: Image analysis service instance.
    """
    return ImageAnalysisService(
        ai_service=ai_service,
        file_validator=file_validator,
        analysis_repository=analysis_repository,
    )
