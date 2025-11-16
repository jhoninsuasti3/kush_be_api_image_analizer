"""Global exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions.

    Args:
        request: The incoming request.
        exc: The application exception.

    Returns:
        JSONResponse with error details.
    """
    logger.error(
        "app_exception_caught",
        exception_type=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions.

    Args:
        request: The incoming request.
        exc: The unhandled exception.

    Returns:
        JSONResponse with generic error message.
    """
    logger.error(
        "unhandled_exception",
        exception_type=exc.__class__.__name__,
        message=str(exc),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred",
            "status_code": 500,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, general_exception_handler)  # type: ignore[arg-type]

    logger.info("exception_handlers_configured")
