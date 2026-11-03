import uuid

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd


async def _seed_hotel_and_room(db, *, quantity=2):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Hotel {suffix}", location="Test"))
    await db.commit()
    room = await db.rooms.add(
        RoomAdd(
            hotel_id=hotel.id,
            title=f"Room {suffix}",
            description="test room",
            price=1000,
            quantity=quantity,
        )
    )
    await db.commit()
    return hotel, room


async def test_get_rooms_and_get_one(ac, db):
    hotel, room = await _seed_hotel_and_room(db)

    listing = await ac.get(
        f"/hotels/{hotel.id}/rooms",
        params={"date_from": "2027-02-01", "date_to": "2027-02-03"},
    )
    assert listing.status_code == 200
    assert any(item["id"] == room.id for item in listing.json())

    one = await ac.get(f"/hotels/{hotel.id}/rooms/{room.id}")
    assert one.status_code == 200
    assert one.json()["id"] == room.id


async def test_create_room(ac, db):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Create Hotel {suffix}", location="Test"))
    await db.commit()

    response = await ac.post(
        f"/hotels/{hotel.id}/rooms",
        json={
            "title": f"Created room {suffix}",
            "description": "created through API",
            "price": 1500,
            "quantity": 2,
            "facilities_ids": [],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["hotel_id"] == hotel.id


async def test_put_and_patch_room(ac, db):
    hotel, room = await _seed_hotel_and_room(db)

    put_response = await ac.put(
        f"/hotels/{hotel.id}/rooms/{room.id}",
        json={
            "title": "PUT room",
            "description": "put",
            "price": 2000,
            "quantity": 3,
            "facilities_ids": [],
        },
    )
    assert put_response.status_code == 200

    patch_response = await ac.patch(
        f"/hotels/{hotel.id}/rooms/{room.id}",
        json={"price": 2500},
    )
    assert patch_response.status_code == 200

    one = await ac.get(f"/hotels/{hotel.id}/rooms/{room.id}")
    assert one.status_code == 200
    assert one.json()["title"] == "PUT room"
    assert one.json()["price"] == 2500


async def test_delete_room_without_bookings(ac, db):
    hotel, room = await _seed_hotel_and_room(db)

    response = await ac.delete(f"/hotels/{hotel.id}/rooms/{room.id}")
    assert response.status_code == 200

    missing = await ac.get(f"/hotels/{hotel.id}/rooms/{room.id}")
    assert missing.status_code == 404
