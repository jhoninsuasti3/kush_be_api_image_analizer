"""Authentication service for user registration and login.

This module provides the business logic for user authentication operations.
"""

from app.core.exceptions import InactiveUserException, InvalidCredentialsException, UserAlreadyExistsException
from app.core.logging import get_logger
from app.core.security import create_token_for_user, get_password_hash, verify_password
from app.domain.models import Token, User, UserCreate, UserLogin
from app.domain.ports import IUserRepository

logger = get_logger(__name__)


class AuthService:
    """Authentication service.

    Handles user registration, login, and token generation.
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize the auth service.

        Args:
            user_repository: Repository for user persistence.
        """
        self.user_repository = user_repository

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user.

        Args:
            user_data: User registration data (email and password).

        Returns:
            User: The created user.

        Raises:
            UserAlreadyExistsException: If a user with this email already exists.
        """
        logger.info("user_registration_started", email=user_data.email)

        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            logger.warning("user_registration_failed_already_exists", email=user_data.email)
            raise UserAlreadyExistsException(f"User with email {user_data.email} already exists")

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create user model
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
        )

        # Save user to repository
        created_user = await self.user_repository.create(user)

        logger.info("user_registered_successfully", email=created_user.email)
        return created_user

    async def login(self, credentials: UserLogin) -> Token:
        """Authenticate a user and generate access token.

        Args:
            credentials: User login credentials (email and password).

        Returns:
            Token: JWT access token.

        Raises:
            InvalidCredentialsException: If credentials are invalid.
            InactiveUserException: If user account is inactive.
        """
        logger.info("user_login_attempt", email=credentials.email)

        # Get user from repository
        user = await self.user_repository.get_by_email(credentials.email)

        # Verify user exists
        if not user:
            logger.warning("login_failed_user_not_found", email=credentials.email)
            raise InvalidCredentialsException("Invalid email or password")

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            logger.warning("login_failed_invalid_password", email=credentials.email)
            raise InvalidCredentialsException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            logger.warning("login_failed_inactive_user", email=credentials.email)
            raise InactiveUserException("User account is inactive")

        # Generate access token
        access_token = create_token_for_user(user.email)

        logger.info("user_logged_in_successfully", email=user.email)

        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(self, email: str) -> User:
        """Get current user by email from token.

        Args:
            email: User email extracted from JWT token.

        Returns:
            User: The current user.

        Raises:
            InvalidCredentialsException: If user not found or inactive.
        """
        user = await self.user_repository.get_by_email(email)

        if not user:
            logger.warning("current_user_not_found", email=email)
            raise InvalidCredentialsException("Could not validate credentials")

        if not user.is_active:
            logger.warning("current_user_inactive", email=email)
            raise InactiveUserException("User account is inactive")

        return user
