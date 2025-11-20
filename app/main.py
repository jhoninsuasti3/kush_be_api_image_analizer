"""Main entry point for the Kush Image Analyzer API.

This is the root FastAPI application that mounts the versioned APIs.
"""

from fastapi import FastAPI
from mangum import Mangum

from app.config.exception_handlers import setup_exception_handlers
from app.config.middlewares import setup_middlewares
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.v1.main import app_v1

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Create main FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for intelligent image analysis with AI",
    version="1.0.0",
    docs_url=settings.docs_url if settings.enable_docs else None,
    redoc_url=settings.redoc_url if settings.enable_docs else None,
)

# Setup middlewares
setup_middlewares(app)

# Setup exception handlers
setup_exception_handlers(app)

# Mount v1 API
app.mount("/api/v1", app_v1)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information.

    Returns:
        dict: API information.
    """
    return {
        "message": "Kush Image Analyzer API",
        "version": "1.0.0",
        "docs": "/docs" if settings.enable_docs else "disabled",
        "v1": "/api/v1",
    }


# AWS Lambda handler (for serverless deployment)
handler = Mangum(app, lifespan="off")

logger.info(
    "application_started",
    environment=settings.environment,
    debug=settings.debug,
)
