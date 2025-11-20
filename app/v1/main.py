"""FastAPI application for API v1."""

from fastapi import FastAPI

from app.core.config import settings
from app.v1.views import analyze, auth, health

# Create FastAPI app for v1
app_v1 = FastAPI(
    title=f"{settings.app_name} - API v1",
    description="Image analysis API with Google Cloud Vision",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
)

# Include routers
app_v1.include_router(health.router)
app_v1.include_router(auth.router)
app_v1.include_router(analyze.router)
