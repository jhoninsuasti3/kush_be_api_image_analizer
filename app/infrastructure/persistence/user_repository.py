"""DynamoDB implementation of IUserRepository.

This module provides the concrete implementation of the user repository
using AWS DynamoDB as the persistence layer.
"""

from datetime import datetime
from typing import Any

from app.core.exceptions import DatabaseException, UserAlreadyExistsException, UserNotFoundException
from app.core.logging import get_logger
from app.domain.models import User
from app.domain.ports import IUserRepository
from app.infrastructure.persistence.dynamodb_client import get_users_table

logger = get_logger(__name__)


class DynamoDBUserRepository(IUserRepository):
    """DynamoDB implementation of the user repository.

    This class provides CRUD operations for users using DynamoDB as the
    persistence layer.
    """

    def __init__(self, table: Any | None = None) -> None:
        """Initialize the repository with a DynamoDB table."""
        self.table = table or get_users_table()

    def create(self, user: User) -> User:
        """Create a new user in DynamoDB.

        Args:
            user: The user to create.

        Returns:
            User: The created user.

        Raises:
            UserAlreadyExistsException: If a user with this email already exists.
            DatabaseException: If database operation fails.
        """
        try:
            # Check if user already exists
            if self.exists(user.email):
                logger.warning("user_already_exists", email=user.email)
                raise UserAlreadyExistsException(f"User with email {user.email} already exists")

            # Prepare item for DynamoDB
            item = {
                "email": user.email,
                "name": user.name,
                "hashed_password": user.hashed_password,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
            }

            # Put item in DynamoDB
            self.table.put_item(Item=item)

            logger.info("user_created", email=user.email)
            return user

        except UserAlreadyExistsException:
            raise
        except Exception as e:
            logger.error("user_create_failed", email=user.email, error=str(e))
            raise DatabaseException(f"Failed to create user: {e}") from e

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email from DynamoDB.

        Args:
            email: The user's email address.

        Returns:
            User | None: The user if found, None otherwise.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            response = self.table.get_item(Key={"email": email})

            if "Item" not in response:
                logger.debug("user_not_found", email=email)
                return None

            item = response["Item"]

            # Convert DynamoDB item to User model
            user = User(
                email=item["email"],
                name=item.get("name", "Unknown"),  # Retrocompatibilidad para usuarios antiguos
                hashed_password=item["hashed_password"],
                is_active=item.get("is_active", True),
                created_at=datetime.fromisoformat(item["created_at"]),
            )

            logger.debug("user_retrieved", email=email)
            return user

        except Exception as e:
            logger.error("user_get_failed", email=email, error=str(e))
            raise DatabaseException(f"Failed to get user: {e}") from e

    def update(self, user: User) -> User:
        """Update an existing user in DynamoDB.

        Args:
            user: The user with updated information.

        Returns:
            User: The updated user.

        Raises:
            UserNotFoundException: If the user doesn't exist.
            DatabaseException: If database operation fails.
        """
        try:
            # Check if user exists
            existing_user = self.get_by_email(user.email)
            if not existing_user:
                logger.warning("user_not_found_for_update", email=user.email)
                raise UserNotFoundException(f"User with email {user.email} not found")

            # Update item in DynamoDB
            self.table.update_item(
                Key={"email": user.email},
                UpdateExpression="SET hashed_password = :password, is_active = :active",
                ExpressionAttributeValues={
                    ":password": user.hashed_password,
                    ":active": user.is_active,
                },
            )

            logger.info("user_updated", email=user.email)
            return user

        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error("user_update_failed", email=user.email, error=str(e))
            raise DatabaseException(f"Failed to update user: {e}") from e

    def delete(self, email: str) -> bool:
        """Delete a user by email from DynamoDB.

        Args:
            email: The user's email address.

        Returns:
            bool: True if the user was deleted, False if not found.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            # Check if user exists before deleting
            if not self.exists(email):
                logger.debug("user_not_found_for_delete", email=email)
                return False

            # Delete item from DynamoDB
            self.table.delete_item(Key={"email": email})

            logger.info("user_deleted", email=email)
            return True

        except Exception as e:
            logger.error("user_delete_failed", email=email, error=str(e))
            raise DatabaseException(f"Failed to delete user: {e}") from e

    def exists(self, email: str) -> bool:
        """Check if a user exists by email.

        Args:
            email: The user's email address.

        Returns:
            bool: True if the user exists, False otherwise.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            user = self.get_by_email(email)
            return user is not None

        except DatabaseException:
            raise
        except Exception as e:
            logger.error("user_exists_check_failed", email=email, error=str(e))
            raise DatabaseException(f"Failed to check if user exists: {e}") from e
