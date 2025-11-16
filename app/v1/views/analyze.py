"""Image analysis endpoints for API v1."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.application.services.image_analysis_service import ImageAnalysisService
from app.core.exceptions import (
    AIServiceException,
    AIServiceRateLimitException,
    AIServiceUnavailableException,
    FileValidationException,
    NoLabelsDetectedException,
)
from app.core.logging import get_logger
from app.domain.models import User
from app.v1.dependencies.auth import get_current_user
from app.v1.dependencies.services import get_image_analysis_service
from app.v1.serializers.analyze import ImageAnalysisResult

logger = get_logger(__name__)

router = APIRouter(prefix="/analyze", tags=["image-analysis"])


@router.post(
    "",
    response_model=ImageAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze image",
    description="Upload an image and get AI-generated tags with confidence scores",
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file to analyze (jpg, jpeg, png, webp)"),
    current_user: User = Depends(get_current_user),
    analysis_service: ImageAnalysisService = Depends(get_image_analysis_service),
) -> ImageAnalysisResult:
    """Analyze an uploaded image and return detected tags.

    Args:
        file: Uploaded image file.
        current_user: Authenticated user from JWT token.
        analysis_service: Injected image analysis service.

    Returns:
        ImageAnalysisResult: Analysis result with detected tags and confidence scores.

    Raises:
        HTTPException 400: If file validation fails.
        HTTPException 413: If file is too large.
        HTTPException 422: If no labels detected.
        HTTPException 429: If rate limit exceeded.
        HTTPException 502: If AI service error.
        HTTPException 503: If AI service unavailable.
    """
    try:
        # Read file content
        file_content = await file.read()

        logger.info(
            "image_analysis_request",
            user_email=current_user.email,
            filename=file.filename,
            content_type=file.content_type,
            size_kb=len(file_content) / 1024,
        )

        # Analyze the image
        result = await analysis_service.analyze_image(
            file_content=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            user_email=current_user.email,
        )

        logger.info(
            "image_analysis_success",
            user_email=current_user.email,
            tags_count=len(result.tags),
        )

        return result

    except FileValidationException as e:
        logger.warning(
            "image_analysis_validation_failed",
            user_email=current_user.email,
            error=str(e),
        )
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e),
        ) from e

    except NoLabelsDetectedException as e:
        logger.warning(
            "image_analysis_no_labels",
            user_email=current_user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    except AIServiceRateLimitException as e:
        logger.error(
            "image_analysis_rate_limit",
            user_email=current_user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        ) from e

    except AIServiceUnavailableException as e:
        logger.error(
            "image_analysis_service_unavailable",
            user_email=current_user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e

    except AIServiceException as e:
        logger.error(
            "image_analysis_ai_error",
            user_email=current_user.email,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error(
            "image_analysis_unexpected_error",
            user_email=current_user.email,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze image",
        ) from e
