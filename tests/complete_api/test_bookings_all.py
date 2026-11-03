import uuid

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd


async def _seed_room(db, quantity=1):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Booking Hotel {suffix}", location="Test"))
    await db.commit()
    room = await db.rooms.add(
        RoomAdd(
            hotel_id=hotel.id,
            title=f"Booking Room {suffix}",
            description=None,
            price=5000,
            quantity=quantity,
        )
    )
    await db.commit()
    return hotel, room


async def test_bookings_require_auth(ac):
    ac.cookies.clear()
    response = await ac.post(
        "/bookings",
        json={"room_id": 1, "date_from": "2027-03-01", "date_to": "2027-03-03"},
    )
    assert response.status_code == 401


async def test_booking_create_get_me_and_get_all(authenticated_ac, db):
    _, room = await _seed_room(db, quantity=1)

    created = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room.id, "date_from": "2027-03-01", "date_to": "2027-03-03"},
    )
    assert created.status_code == 200
    booking_id = created.json()["data"]["id"]
    assert created.json()["data"]["price"] == room.price

    mine = await authenticated_ac.get("/bookings/me")
    assert mine.status_code == 200
    assert any(item["id"] == booking_id for item in mine.json())

    all_bookings = await authenticated_ac.get("/bookings")
    assert all_bookings.status_code == 200
    assert any(item["id"] == booking_id for item in all_bookings.json())

    second = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room.id, "date_from": "2027-03-01", "date_to": "2027-03-03"},
    )
    assert second.status_code == 409


async def test_booking_date_validation(authenticated_ac, db):
    _, room = await _seed_room(db)

    reversed_dates = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room.id, "date_from": "2027-03-05", "date_to": "2027-03-03"},
    )
    assert reversed_dates.status_code == 400

    same_dates = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room.id, "date_from": "2027-03-05", "date_to": "2027-03-05"},
    )
    assert same_dates.status_code == 400
