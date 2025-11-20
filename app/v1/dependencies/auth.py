"""Authentication dependencies for FastAPI.

Provides dependency injection for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.services.auth_service import AuthService
from app.core.logging import get_logger
from app.core.security import get_email_from_token
from app.domain.models import User
from app.infrastructure.persistence.user_repository import DynamoDBUserRepository

logger = get_logger(__name__)

# Security scheme for JWT
security = HTTPBearer()


def get_user_repository() -> DynamoDBUserRepository:
    """Get user repository instance.

    Returns:
        DynamoDBUserRepository: User repository instance.
    """
    return DynamoDBUserRepository()


def get_auth_service(
    user_repository: DynamoDBUserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get auth service instance.

    Args:
        user_repository: Injected user repository.

    Returns:
        AuthService: Auth service instance.
    """
    return AuthService(user_repository=user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials (Bearer token).
        auth_service: Injected auth service.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If authentication fails.
    """
    token = credentials.credentials

    # Extract email from token
    email = get_email_from_token(token)

    if email is None:
        logger.warning("invalid_token_in_request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    try:
        user = await run_in_threadpool(auth_service.get_current_user, email)
        return user
    except Exception as e:
        logger.error("get_current_user_failed", email=email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
