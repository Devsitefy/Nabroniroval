import pytest

from src.exceptions import InvalidTokenException
from src.services.auth import AuthService


def test_hash_and_verify_password():
    service = AuthService()
    hashed = service.hash_password("secret")
    assert hashed != "secret"
    assert service.verify_password("secret", hashed) is True
    assert service.verify_password("wrong", hashed) is False


def test_token_roundtrip():
    service = AuthService()
    token = service.create_access_token({"user_id": 123})
    payload = service.decode_token(token)
    assert payload["user_id"] == 123
    assert "exp" in payload


def test_invalid_token_raises_domain_exception():
    with pytest.raises(InvalidTokenException):
        AuthService().decode_token("definitely-not-a-jwt")
