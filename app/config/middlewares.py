"""Global middlewares for the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        """Log request and response information.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.

        Returns:
            Response from the next handler.
        """
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        # Process request
        response = await call_next(request)

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )

        return response


def setup_middlewares(app: FastAPI) -> None:
    """Configure all middlewares for the application.

    Args:
        app: The FastAPI application instance.
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging middleware
    app.add_middleware(LoggingMiddleware)

    logger.info(
        "middlewares_configured",
        cors_origins=settings.cors_origins_list,
    )
