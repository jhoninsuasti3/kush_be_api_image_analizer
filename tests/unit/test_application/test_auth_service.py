"""Tests for AuthService."""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.application.services.auth_service import AuthService
from app.core.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.domain.models import User, UserCreate, UserLogin
from app.domain.ports import IUserRepository


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def mock_user_repository(self) -> Mock:
        """Create mock user repository."""
        return Mock(spec=IUserRepository)

    @pytest.fixture
    def auth_service(self, mock_user_repository: Mock) -> AuthService:
        """Create AuthService instance with mocked repository."""
        return AuthService(user_repository=mock_user_repository)

    @pytest.fixture
    def user_create_data(self) -> UserCreate:
        """Create user registration data."""
        return UserCreate(email="test@example.com", password="StrongPassword123!")

    @pytest.fixture
    def existing_user(self) -> User:
        """Create an existing user."""
        return User(
            email="existing@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyAJ3xIqP4iq",  # "password123"
            is_active=True,
        )

    # ========================================================================
    # Register Tests
    # ========================================================================

    def test_register_success(
        self, auth_service: AuthService, user_create_data: UserCreate, mock_user_repository: Mock
    ) -> None:
        """Test successful user registration."""
        # Mock repository responses
        mock_user_repository.exists.return_value = False
        mock_user_repository.create.return_value = User(
            email=user_create_data.email,
            hashed_password="hashed_password",
            is_active=True,
        )

        # Register user
        with patch("app.application.services.auth_service.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = auth_service.register(user_create_data)

        # Verify
        assert user.email == user_create_data.email
        assert user.is_active is True
        mock_user_repository.exists.assert_called_once_with(user_create_data.email)
        mock_user_repository.create.assert_called_once()
        mock_hash.assert_called_once_with(user_create_data.password)

    def test_register_user_already_exists(
        self, auth_service: AuthService, user_create_data: UserCreate, mock_user_repository: Mock
    ) -> None:
        """Test registration fails when user already exists."""
        mock_user_repository.exists.return_value = True

        with pytest.raises(UserAlreadyExistsException) as exc_info:
            auth_service.register(user_create_data)

        assert user_create_data.email in str(exc_info.value)
        mock_user_repository.create.assert_not_called()

    def test_register_hashes_password(
        self, auth_service: AuthService, user_create_data: UserCreate, mock_user_repository: Mock
    ) -> None:
        """Test that password is hashed during registration."""
        mock_user_repository.exists.return_value = False

        with patch("app.application.services.auth_service.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password_xyz"
            mock_user_repository.create.return_value = User(
                email=user_create_data.email,
                hashed_password="hashed_password_xyz",
                is_active=True,
            )

            auth_service.register(user_create_data)

            # Verify password was hashed
            mock_hash.assert_called_once_with(user_create_data.password)

            # Verify create was called with hashed password
            create_call_args = mock_user_repository.create.call_args
            created_user = create_call_args[0][0]
            assert created_user.hashed_password == "hashed_password_xyz"

    def test_register_creates_active_user(
        self, auth_service: AuthService, user_create_data: UserCreate, mock_user_repository: Mock
    ) -> None:
        """Test that registered user is active by default."""
        mock_user_repository.exists.return_value = False

        with patch("app.application.services.auth_service.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed"
            mock_user_repository.create.return_value = User(
                email=user_create_data.email,
                hashed_password="hashed",
                is_active=True,
            )

            user = auth_service.register(user_create_data)

            assert user.is_active is True

    # ========================================================================
    # Login Tests
    # ========================================================================

    def test_login_success(
        self, auth_service: AuthService, existing_user: User, mock_user_repository: Mock
    ) -> None:
        """Test successful login."""
        credentials = UserLogin(email=existing_user.email, password="password123")

        mock_user_repository.get_by_email.return_value = existing_user

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = True

            token = auth_service.login(credentials)

            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0

        mock_user_repository.get_by_email.assert_called_once_with(credentials.email)
        mock_verify.assert_called_once_with(credentials.password, existing_user.hashed_password)

    def test_login_user_not_found(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test login fails when user doesn't exist."""
        credentials = UserLogin(email="nonexistent@example.com", password="password123")

        mock_user_repository.get_by_email.side_effect = UserNotFoundException("User not found")

        with pytest.raises(InvalidCredentialsException) as exc_info:
            auth_service.login(credentials)

        assert "invalid" in str(exc_info.value).lower()

    def test_login_wrong_password(
        self, auth_service: AuthService, existing_user: User, mock_user_repository: Mock
    ) -> None:
        """Test login fails with wrong password."""
        credentials = UserLogin(email=existing_user.email, password="wrong_password")

        mock_user_repository.get_by_email.return_value = existing_user

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(InvalidCredentialsException) as exc_info:
                auth_service.login(credentials)

            assert "invalid" in str(exc_info.value).lower()

    def test_login_inactive_user(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test login fails when user is inactive."""
        inactive_user = User(
            email="inactive@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyAJ3xIqP4iq",
            is_active=False,
        )
        credentials = UserLogin(email=inactive_user.email, password="password123")

        mock_user_repository.get_by_email.return_value = inactive_user

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = True

            with pytest.raises(InactiveUserException) as exc_info:
                auth_service.login(credentials)

            assert "inactive" in str(exc_info.value).lower()

    def test_login_generates_valid_jwt_token(
        self, auth_service: AuthService, existing_user: User, mock_user_repository: Mock
    ) -> None:
        """Test that login generates a valid JWT token."""
        credentials = UserLogin(email=existing_user.email, password="password123")

        mock_user_repository.get_by_email.return_value = existing_user

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            with patch("app.application.services.auth_service.create_token_for_user") as mock_create_token:
                mock_verify.return_value = True
                mock_create_token.return_value = "valid.jwt.token"

                token = auth_service.login(credentials)

                assert token == "valid.jwt.token"
                mock_create_token.assert_called_once_with(existing_user)

    # ========================================================================
    # Get Current User Tests
    # ========================================================================

    def test_get_current_user_success(
        self, auth_service: AuthService, existing_user: User, mock_user_repository: Mock
    ) -> None:
        """Test successful retrieval of current user."""
        mock_user_repository.get_by_email.return_value = existing_user

        user = auth_service.get_current_user(existing_user.email)

        assert user.email == existing_user.email
        assert user.is_active is True
        mock_user_repository.get_by_email.assert_called_once_with(existing_user.email)

    def test_get_current_user_not_found(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test get current user fails when user not found."""
        mock_user_repository.get_by_email.side_effect = UserNotFoundException("User not found")

        with pytest.raises(UserNotFoundException):
            auth_service.get_current_user("nonexistent@example.com")

    def test_get_current_user_inactive(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test get current user fails when user is inactive."""
        inactive_user = User(
            email="inactive@example.com",
            hashed_password="hashed",
            is_active=False,
        )
        mock_user_repository.get_by_email.return_value = inactive_user

        with pytest.raises(InactiveUserException) as exc_info:
            auth_service.get_current_user("inactive@example.com")

        assert "inactive" in str(exc_info.value).lower()

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_register_with_email_case_variations(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test registration with different email cases."""
        user_data = UserCreate(email="Test@Example.COM", password="StrongPassword123!")

        mock_user_repository.exists.return_value = False

        with patch("app.application.services.auth_service.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed"
            mock_user_repository.create.return_value = User(
                email=user_data.email,
                hashed_password="hashed",
                is_active=True,
            )

            user = auth_service.register(user_data)

            # Should preserve original email case
            assert user.email == "Test@Example.COM"

    def test_login_verifies_password_before_checking_active_status(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test that password is verified before checking if user is active."""
        inactive_user = User(
            email="inactive@example.com",
            hashed_password="hashed",
            is_active=False,
        )
        credentials = UserLogin(email=inactive_user.email, password="wrong_password")

        mock_user_repository.get_by_email.return_value = inactive_user

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = False

            # Should raise InvalidCredentialsException, not InactiveUserException
            with pytest.raises(InvalidCredentialsException):
                auth_service.login(credentials)

    def test_multiple_login_attempts_different_users(
        self, auth_service: AuthService, mock_user_repository: Mock
    ) -> None:
        """Test multiple login attempts for different users."""
        user1 = User(email="user1@example.com", hashed_password="hash1", is_active=True)
        user2 = User(email="user2@example.com", hashed_password="hash2", is_active=True)

        def get_user_by_email(email: str) -> User:
            if email == user1.email:
                return user1
            elif email == user2.email:
                return user2
            raise UserNotFoundException("User not found")

        mock_user_repository.get_by_email.side_effect = get_user_by_email

        with patch("app.application.services.auth_service.verify_password") as mock_verify:
            with patch("app.application.services.auth_service.create_token_for_user") as mock_create_token:
                mock_verify.return_value = True
                mock_create_token.return_value = "token"

                # Login as user1
                token1 = auth_service.login(UserLogin(email=user1.email, password="pass1"))
                assert token1 == "token"

                # Login as user2
                token2 = auth_service.login(UserLogin(email=user2.email, password="pass2"))
                assert token2 == "token"

                # Verify both users were retrieved
                assert mock_user_repository.get_by_email.call_count == 2