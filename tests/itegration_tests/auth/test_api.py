import pytest


@pytest.mark.parametrize(
    "email, password, status_code, status_register",
    [
        ("volodya1@putin.ru", "molodec", 401, 200),
        ("vladimir@putin.ru", "loh", 401, 409),
        ("vladimir@putin.ru", "molodec", 200, 409),
    ],
)
async def test_authentification(ac, email, password, status_code, status_register):
    if ac.cookies.get("access_token"):
        ac.cookies.delete("access_token")
    response_register = await ac.post(
        "/auth/register", json={"email": "vladimir@putin.ru", "password": "molodec"}
    )
    assert response_register.status_code == status_register

    response_login = await ac.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response_login.status_code == status_code
    if status_code == 200:
        assert ac.cookies.get("access_token")

    response_me = await ac.get("/auth/me")
    assert response_me.status_code == status_code

    response_logout = await ac.post("/auth/logout")
    assert response_logout.status_code == 200
    assert ac.cookies.get("access_token") is None

    response_me = await ac.get("/auth/me")
    assert response_me.status_code == 401
