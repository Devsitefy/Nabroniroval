from src.services.auth import AuthService


def test_create_and_decode_access_token():
    jwt_token = AuthService().create_access_token({"user_id": 1})

    assert jwt_token
    assert isinstance(jwt_token, str)

    payload = AuthService().decode_token(jwt_token)
    assert payload
    assert payload["user_id"] == 1
