"""Unit tests for app.core.security module."""

from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_token_for_user,
    decode_access_token,
    get_email_from_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_different_hash_than_plain(self) -> None:
        """Test that hashed password is different from plain password."""
        plain_password = "mysecretpassword"
        hashed = get_password_hash(plain_password)

        assert hashed != plain_password
        assert len(hashed) > 0

    def test_verify_password_with_correct_password(self) -> None:
        """Test password verification with correct password."""
        plain_password = "mysecretpassword"
        hashed = get_password_hash(plain_password)

        assert verify_password(plain_password, hashed) is True

    def test_verify_password_with_incorrect_password(self) -> None:
        """Test password verification with incorrect password."""
        plain_password = "mysecretpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(plain_password)

        assert verify_password(wrong_password, hashed) is False

    def test_same_password_produces_different_hashes(self) -> None:
        """Test that hashing the same password twice produces different hashes."""
        plain_password = "mysecretpassword"
        hash1 = get_password_hash(plain_password)
        hash2 = get_password_hash(plain_password)

        # Hashes should be different due to different salts
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(plain_password, hash1) is True
        assert verify_password(plain_password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token_returns_string(self) -> None:
        """Test that create_access_token returns a string token."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_returns_payload(self) -> None:
        """Test that decode_access_token returns the correct payload."""
        email = "user@example.com"
        data = {"sub": email}
        token = create_access_token(data)

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == email
        assert "exp" in payload

    def test_decode_invalid_token_returns_none(self) -> None:
        """Test that decoding an invalid token returns None."""
        invalid_token = "invalid.token.here"

        payload = decode_access_token(invalid_token)

        assert payload is None

    def test_create_token_with_custom_expiration(self) -> None:
        """Test creating a token with custom expiration time."""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=60)

        token = create_access_token(data, expires_delta)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user@example.com"

    def test_create_token_for_user(self) -> None:
        """Test creating a token for a specific user."""
        email = "user@example.com"

        token = create_token_for_user(email)

        assert isinstance(token, str)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == email

    def test_get_email_from_token(self) -> None:
        """Test extracting email from a valid token."""
        email = "user@example.com"
        token = create_token_for_user(email)

        extracted_email = get_email_from_token(token)

        assert extracted_email == email

    def test_get_email_from_invalid_token_returns_none(self) -> None:
        """Test extracting email from an invalid token returns None."""
        invalid_token = "invalid.token.here"

        email = get_email_from_token(invalid_token)

        assert email is None

    def test_token_contains_expiration(self) -> None:
        """Test that created token contains an expiration claim."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        payload = decode_access_token(token)

        assert payload is not None
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
