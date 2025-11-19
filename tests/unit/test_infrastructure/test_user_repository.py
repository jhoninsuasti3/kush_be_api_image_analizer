"""Tests for DynamoDBUserRepository."""

from typing import Any

import pytest

from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.domain.models import User
from app.infrastructure.persistence.user_repository import DynamoDBUserRepository


class TestDynamoDBUserRepository:
    """Test suite for DynamoDBUserRepository."""

    @pytest.fixture
    def repository(self, users_table: Any) -> DynamoDBUserRepository:
        """Create repository instance."""
        return DynamoDBUserRepository(users_table)

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(email="test@example.com", hashed_password="hashed_password_123", is_active=True)

    # ========================================================================
    # Create Tests
    # ========================================================================

    def test_create_user_success(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test successful user creation."""
        created_user = repository.create(sample_user)

        assert created_user.email == sample_user.email
        assert created_user.hashed_password == sample_user.hashed_password
        assert created_user.is_active == sample_user.is_active

    def test_create_user_duplicate_email(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test that creating a user with duplicate email raises exception."""
        # Create user first time
        repository.create(sample_user)

        # Try to create again with same email
        with pytest.raises(UserAlreadyExistsException) as exc_info:
            repository.create(sample_user)

        assert "already exists" in str(exc_info.value).lower()

    def test_create_user_with_inactive_status(self, repository: DynamoDBUserRepository) -> None:
        """Test creating an inactive user."""
        inactive_user = User(email="inactive@example.com", hashed_password="hashed_pass", is_active=False)

        created_user = repository.create(inactive_user)

        assert created_user.is_active is False

    # ========================================================================
    # Get By Email Tests
    # ========================================================================

    def test_get_by_email_success(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test successful retrieval of user by email."""
        # Create user first
        repository.create(sample_user)

        # Retrieve user
        retrieved_user = repository.get_by_email(sample_user.email)

        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.hashed_password == sample_user.hashed_password
        assert retrieved_user.is_active == sample_user.is_active

    def test_get_by_email_not_found(self, repository: DynamoDBUserRepository) -> None:
        """Test that getting non-existent user raises exception."""
        with pytest.raises(UserNotFoundException) as exc_info:
            repository.get_by_email("nonexistent@example.com")

        assert "not found" in str(exc_info.value).lower()

    def test_get_by_email_case_sensitive(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test that email lookup is case-sensitive."""
        repository.create(sample_user)

        # Try with different case
        with pytest.raises(UserNotFoundException):
            repository.get_by_email(sample_user.email.upper())

    # ========================================================================
    # Update Tests
    # ========================================================================

    def test_update_user_success(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test successful user update."""
        # Create user
        repository.create(sample_user)

        # Update user
        sample_user.is_active = False
        updated_user = repository.update(sample_user)

        assert updated_user.is_active is False

        # Verify persistence
        retrieved_user = repository.get_by_email(sample_user.email)
        assert retrieved_user.is_active is False

    def test_update_user_not_found(self, repository: DynamoDBUserRepository) -> None:
        """Test updating non-existent user raises exception."""
        non_existent_user = User(email="ghost@example.com", hashed_password="hashed", is_active=True)

        with pytest.raises(UserNotFoundException):
            repository.update(non_existent_user)

    def test_update_user_password(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test updating user password."""
        repository.create(sample_user)

        # Update password
        new_password_hash = "new_hashed_password_456"
        sample_user.hashed_password = new_password_hash
        updated_user = repository.update(sample_user)

        assert updated_user.hashed_password == new_password_hash

    # ========================================================================
    # Delete Tests
    # ========================================================================

    def test_delete_user_success(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test successful user deletion."""
        # Create user
        repository.create(sample_user)

        # Delete user
        repository.delete(sample_user.email)

        # Verify deletion
        with pytest.raises(UserNotFoundException):
            repository.get_by_email(sample_user.email)

    def test_delete_user_not_found(self, repository: DynamoDBUserRepository) -> None:
        """Test deleting non-existent user raises exception."""
        with pytest.raises(UserNotFoundException):
            repository.delete("nonexistent@example.com")

    # ========================================================================
    # Exists Tests
    # ========================================================================

    def test_exists_user_true(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test exists returns True for existing user."""
        repository.create(sample_user)

        assert repository.exists(sample_user.email) is True

    def test_exists_user_false(self, repository: DynamoDBUserRepository) -> None:
        """Test exists returns False for non-existent user."""
        assert repository.exists("nonexistent@example.com") is False

    def test_exists_after_deletion(self, repository: DynamoDBUserRepository, sample_user: User) -> None:
        """Test exists returns False after user deletion."""
        repository.create(sample_user)
        repository.delete(sample_user.email)

        assert repository.exists(sample_user.email) is False

    # ========================================================================
    # Edge Cases and Error Handling
    # ========================================================================

    def test_create_user_with_special_characters_in_email(self, repository: DynamoDBUserRepository) -> None:
        """Test creating user with special characters in email."""
        special_user = User(email="test+tag@example.co.uk", hashed_password="hashed_password", is_active=True)

        created_user = repository.create(special_user)
        assert created_user.email == special_user.email

    def test_multiple_users_creation(self, repository: DynamoDBUserRepository, user_factory: type) -> None:
        """Test creating multiple users."""
        users = user_factory.create_batch(5)

        for user in users:
            created = repository.create(user)
            assert created.email == user.email

        # Verify all exist
        for user in users:
            assert repository.exists(user.email) is True

    def test_repository_handles_empty_table(self, repository: DynamoDBUserRepository) -> None:
        """Test repository operations on empty table."""
        # Should not raise exception
        assert repository.exists("anyone@example.com") is False

        with pytest.raises(UserNotFoundException):
            repository.get_by_email("anyone@example.com")
