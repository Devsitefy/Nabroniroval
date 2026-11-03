import json
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()


mock.patch("fastapi_cache.FastAPICache.clear", new_callable=mock.AsyncMock).start()
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert, delete

from src.config import settings
from src.database import Base, async_session_maker, engine
from src.main import app
from src.models import *
from src.utils.db_manager import DBManager


@pytest.fixture(scope="function")
async def db() -> DBManager:
    async with DBManager(session_factory=async_session_maker) as db:
        yield db



@pytest.fixture(scope="module")
async def delete_all_bookings():
    async with async_session_maker() as session:
        await session.execute(
            delete(BookingsOrm)
        )
        await session.commit()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        with open("tests/mock_hotels.json", encoding="utf-8") as f:
            hotels = json.load(f)
        with open("tests/mock_rooms.json", encoding="utf-8") as f:
            rooms = json.load(f)
        await conn.execute(insert(HotelsOrm).values(hotels))
        await conn.execute(insert(RoomsOrm).values(rooms))


@pytest.fixture(scope="function")
async def ac(setup_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "volodya@putin.ru",
                "password": "molodec",
            },
        )
        assert response.status_code == 200


@pytest.fixture(scope="function")
async def authenticated_ac(register_user, ac):
    response = await ac.post(
        "/auth/login", json={"email": "volodya@putin.ru", "password": "molodec"}
    )
    assert response.status_code == 200
    assert ac.cookies.get("access_token")
    yield ac
