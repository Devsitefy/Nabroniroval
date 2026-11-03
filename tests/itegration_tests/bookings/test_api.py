import pytest

from src.database import async_session_maker
from src.utils.db_manager import DBManager




@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code, quantity",
    [
        (1, "2026-09-10", "2026-09-30", 200, 1),
        (1, "2026-09-10", "2026-09-30", 200, 2),
        (1, "2026-09-10", "2026-09-30", 200, 3),
        (1, "2026-09-10", "2026-09-30", 409, 3),
    ],
)
async def test_add_and_get_my_bookings(
    delete_all_bookings,
    db,
    authenticated_ac,
    room_id,
    date_from,
    date_to,
    status_code,
    quantity,
):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        my_bookings = await authenticated_ac.get("/bookings/me")
        assert my_bookings.status_code == 200
        assert quantity == len(my_bookings.json())

        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res
