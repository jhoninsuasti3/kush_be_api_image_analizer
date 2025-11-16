"""Authentication endpoints for API v1."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.auth_service import AuthService
from app.core.exceptions import InactiveUserException, InvalidCredentialsException, UserAlreadyExistsException
from app.core.logging import get_logger
from app.domain.models import User
from app.v1.dependencies.auth import get_auth_service, get_current_user
from app.v1.serializers.auth import Token, UserCreate, UserLogin, UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user.

    Args:
        user_data: User registration data (email and password).
        auth_service: Injected authentication service.

    Returns:
        UserResponse: Created user information (without password).

    Raises:
        HTTPException 409: If user already exists.
        HTTPException 500: If registration fails.
    """
    try:
        user = await auth_service.register(user_data)

        logger.info("user_registered_via_api", email=user.email)

        return UserResponse(
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    except UserAlreadyExistsException as e:
        logger.warning("registration_failed_user_exists", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error("registration_failed", email=user_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from e


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive JWT access token",
)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authenticate user and generate access token.

    Args:
        credentials: User login credentials (email and password).
        auth_service: Injected authentication service.

    Returns:
        Token: JWT access token.

    Raises:
        HTTPException 401: If credentials are invalid.
        HTTPException 403: If user account is inactive.
        HTTPException 500: If login fails.
    """
    try:
        token = await auth_service.login(credentials)

        logger.info("user_logged_in_via_api", email=credentials.email)

        return token

    except InvalidCredentialsException as e:
        logger.warning("login_failed_invalid_credentials", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except InactiveUserException as e:
        logger.warning("login_failed_inactive_user", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error("login_failed", email=credentials.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login",
        ) from e


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get information about the currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Injected current user from JWT token.

    Returns:
        UserResponse: Current user information.
    """
    logger.debug("get_current_user_info", email=current_user.email)

    return UserResponse(
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
