"""Lambda handler for image analysis endpoints.

This Lambda handles image analysis operations:
- POST /api/v1/analyze - Upload and analyze image

Optimized for image processing with higher memory allocation.
"""

from mangum import Mangum

from app.core.logging import configure_logging, get_logger

# Configure logging before creating the app
configure_logging()
logger = get_logger(__name__)


def create_analyze_app():
    """Create minimal FastAPI app for analyze endpoints only.

    Lazy loading to optimize cold start.
    """
    from fastapi import FastAPI

    from app.config.exception_handlers import setup_exception_handlers
    from app.config.middlewares import setup_middlewares
    from app.core.config import settings
    from app.v1.views.analyze import router as analyze_router

    app = FastAPI(
        title=f"{settings.app_name} - Analysis Service",
        description="Image analysis and AI processing microservice",
        version="1.0.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )

    # Setup middlewares
    setup_middlewares(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include only analyze router
    app.include_router(analyze_router, prefix="/api/v1", tags=["analysis"])

    # Health check for this Lambda
    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Health check for analysis service with AI service status."""
        from app.v1.dependencies.services import get_ai_service

        ai_service = get_ai_service()
        ai_healthy = await ai_service.health_check()

        return {
            "service": "analysis",
            "status": "healthy" if ai_healthy else "degraded",
            "ai_service": "healthy" if ai_healthy else "unhealthy",
        }

    logger.info(
        "analysis_lambda_initialized",
        environment=settings.environment,
        service="analysis",
    )

    return app


# Create app instance (reused across warm invocations)
app = create_analyze_app()

# AWS Lambda handler
lambda_handler = Mangum(app, lifespan="off")