"""Security utilities for JWT authentication and password hashing.

This module provides functions for:
- Password hashing and verification using bcrypt
- JWT token creation and validation
- User authentication
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary containing claims to encode in the token.
        expires_delta: Optional custom expiration time delta.
                      If not provided, uses settings.access_token_expire_minutes.

    Returns:
        str: The encoded JWT token.

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> # Token will expire in 30 minutes (default)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode.

    Returns:
        dict | None: The decoded token payload if valid, None otherwise.

    Example:
        >>> payload = decode_access_token(token)
        >>> if payload:
        ...     user_email = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def create_token_for_user(user_or_email: str | Any) -> str:
    """Create an access token for a user.

    Args:
        user_or_email: The user's email address or an object with an `email` attribute.

    Returns:
        str: The encoded JWT token with the user's email as the subject.

    Example:
        >>> token = create_token_for_user("user@example.com")
    """
    email: str | None = user_or_email if isinstance(user_or_email, str) else getattr(user_or_email, "email", None)

    if not isinstance(email, str):
        raise ValueError("A valid email address is required to create a token")

    return create_access_token(data={"sub": email})


def get_email_from_token(token: str) -> str | None:
    """Extract the email (subject) from a JWT token.

    Args:
        token: The JWT token to decode.

    Returns:
        str | None: The email if the token is valid, None otherwise.

    Example:
        >>> email = get_email_from_token(token)
        >>> if email:
        ...     # User is authenticated
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload.get("sub")
