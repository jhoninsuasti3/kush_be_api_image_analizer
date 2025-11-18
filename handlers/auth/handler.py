"""Lambda handler for authentication endpoints.

This Lambda handles all authentication operations:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login
- GET /api/v1/auth/me - Get current user

Optimized for cold start performance.
"""

from mangum import Mangum

from app.core.logging import configure_logging, get_logger

# Configure logging before creating the app
configure_logging()
logger = get_logger(__name__)


def create_auth_app():
    """Create minimal FastAPI app for auth endpoints only.

    Lazy loading to optimize cold start.
    """
    from fastapi import FastAPI

    from app.config.exception_handlers import setup_exception_handlers
    from app.config.middlewares import setup_middlewares
    from app.core.config import settings
    from app.v1.views.auth import router as auth_router

    app = FastAPI(
        title=f"{settings.app_name} - Auth Service",
        description="Authentication and user management microservice",
        version="1.0.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )

    # Setup middlewares
    setup_middlewares(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include only auth router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

    # Health check for this Lambda
    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Health check for auth service."""
        return {"service": "auth", "status": "healthy"}

    logger.info(
        "auth_lambda_initialized",
        environment=settings.environment,
        service="auth",
    )

    return app


# Create app instance (reused across warm invocations)
app = create_auth_app()

# AWS Lambda handler
lambda_handler = Mangum(app, lifespan="off")