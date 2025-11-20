"""Health check endpoints for API v1."""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.persistence.dynamodb_client import get_users_table

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status", examples=["healthy"])
    service: str = Field(..., description="Service name")
    environment: str = Field(..., description="Environment")
    timestamp: datetime = Field(..., description="Current timestamp")


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    status: str = Field(..., description="Readiness status", examples=["ready"])
    checks: dict[str, str] = Field(..., description="Individual service checks")
    timestamp: datetime = Field(..., description="Current timestamp")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the API",
)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        HealthResponse: Health status information.
    """
    logger.debug("health_check_called")

    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        environment=settings.environment,
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Returns readiness status including dependency checks",
)
async def readiness_check() -> ReadinessResponse:
    """Readiness check endpoint with dependency verification.

    Checks:
    - DynamoDB connection

    Returns:
        ReadinessResponse: Readiness status with individual checks.
    """
    logger.debug("readiness_check_called")

    checks: dict[str, str] = {}

    # Check DynamoDB
    try:
        table = get_users_table()
        table.load()
        checks["database"] = "healthy"
        logger.debug("dynamodb_ready_check_passed")
    except Exception as e:
        checks["database"] = "unhealthy"
        logger.error("dynamodb_ready_check_failed", error=str(e))

    # Overall status
    overall_status = "ready" if all(check == "healthy" for check in checks.values()) else "not ready"

    logger.info("readiness_check_completed", status=overall_status, checks=checks)

    return ReadinessResponse(
        status=overall_status,
        checks=checks,
        timestamp=datetime.utcnow(),
    )
