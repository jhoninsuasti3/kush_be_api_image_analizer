"""Lambda handler for health check endpoints.

This Lambda handles system health and readiness checks:
- GET /api/v1/health - Basic health check
- GET /api/v1/ready - Readiness check with dependencies

Lightweight and fast-responding.
"""

from mangum import Mangum

from app.core.logging import configure_logging, get_logger

# Configure logging before creating the app
configure_logging()
logger = get_logger(__name__)


def create_health_app():
    """Create minimal FastAPI app for health endpoints only.

    Lazy loading to optimize cold start.
    """
    from fastapi import FastAPI

    from app.config.exception_handlers import setup_exception_handlers
    from app.config.middlewares import setup_middlewares
    from app.core.config import settings
    from app.v1.views.health import router as health_router

    app = FastAPI(
        title=f"{settings.app_name} - Health Service",
        description="Health monitoring and status microservice",
        version="1.0.0",
        docs_url=None,  # No docs for health service
        redoc_url=None,
    )

    # Setup minimal middlewares for health checks
    setup_middlewares(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include only health router
    app.include_router(health_router, prefix="/api/v1", tags=["health"])

    logger.info(
        "health_lambda_initialized",
        environment=settings.environment,
        service="health",
    )

    return app


# Create app instance (reused across warm invocations)
app = create_health_app()

# AWS Lambda handler
lambda_handler = Mangum(app, lifespan="off")