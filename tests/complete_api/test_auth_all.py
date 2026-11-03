import uuid


async def test_register_login_me_logout_full_flow(ac):
    ac.cookies.clear()
    email = f"test-{uuid.uuid4().hex}@example.com"
    password = "strong-password"

    register = await ac.post("/auth/register", json={"email": email, "password": password})
    assert register.status_code == 200
    assert register.json() == {"status": "ok"}

    duplicate = await ac.post("/auth/register", json={"email": email, "password": password})
    assert duplicate.status_code == 409

    wrong_password = await ac.post("/auth/login", json={"email": email, "password": "wrong"})
    assert wrong_password.status_code == 401

    unknown_user = await ac.post(
        "/auth/login",
        json={"email": f"missing-{uuid.uuid4().hex}@example.com", "password": password},
    )
    assert unknown_user.status_code == 401

    login = await ac.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    assert login.json()["access_token"]
    assert ac.cookies.get("access_token")

    me = await ac.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == email

    logout = await ac.post("/auth/logout")
    assert logout.status_code == 200
    assert ac.cookies.get("access_token") is None

    unauthorized = await ac.get("/auth/me")
    assert unauthorized.status_code == 401
