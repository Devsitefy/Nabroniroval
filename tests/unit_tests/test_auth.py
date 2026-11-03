from src.services.auth import AuthService


def test_create_access_token():
    jwt_token = AuthService().create_access_token({"user_id": 1})

    assert jwt_token
    assert isinstance(jwt_token, str)
