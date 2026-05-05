"""Unit tests for core.security — password hashing and JWT helpers."""

import pytest
from jose import JWTError

from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for bcrypt hash/verify helpers."""

    def test_hash_returns_string(self) -> None:
        assert isinstance(hash_password("secret"), str)

    def test_hash_is_not_plaintext(self) -> None:
        assert hash_password("secret") != "secret"

    def test_verify_correct_password(self) -> None:
        hashed = hash_password("correct-horse")
        assert verify_password("correct-horse", hashed) is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("correct-horse")
        assert verify_password("wrong-password", hashed) is False

    def test_unique_hashes_per_call(self) -> None:
        """bcrypt generates a fresh salt each time."""
        assert hash_password("same") != hash_password("same")

    def test_minimum_length_enforcement(self) -> None:
        """Passwords shorter than 8 characters should fail schema validation,
        but security helpers themselves accept any non-empty string."""
        hashed = hash_password("short")
        assert verify_password("short", hashed) is True


class TestJwtTokens:
    """Tests for JWT creation and decoding."""

    def test_access_token_sub_claim(self) -> None:
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"

    def test_access_token_type_claim(self) -> None:
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_refresh_token_type_claim(self) -> None:
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_decode_invalid_token_raises(self) -> None:
        with pytest.raises(JWTError):
            decode_token("not.a.valid.token")

    def test_decode_tampered_token_raises(self) -> None:
        token = create_access_token("user-789")
        tampered = token[:-4] + "XXXX"
        with pytest.raises(JWTError):
            decode_token(tampered)
