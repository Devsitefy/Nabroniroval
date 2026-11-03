from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.exceptions import CheckInDateLaterThanCheckOutException
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService


async def test_add_booking_locks_room_before_insert():
    events = []
    room = SimpleNamespace(id=10, price=7777, quantity=1)

    rooms = SimpleNamespace(get_one_for_update=AsyncMock())
    bookings = SimpleNamespace(add_booking=AsyncMock())
    db = SimpleNamespace(rooms=rooms, bookings=bookings, commit=AsyncMock())

    async def lock_room(**kwargs):
        events.append("lock")
        return room

    async def add_booking(data):
        events.append("insert")
        return SimpleNamespace(id=1, **data.model_dump())

    async def commit():
        events.append("commit")

    rooms.get_one_for_update.side_effect = lock_room
    bookings.add_booking.side_effect = add_booking
    db.commit.side_effect = commit

    data = BookingAddRequest(room_id=10, date_from=date(2027, 1, 1), date_to=date(2027, 1, 3))
    result = await BookingService(db).add_booking(user_id=5, booking_data=data)

    assert result.price == 7777
    assert events == ["lock", "insert", "commit"]
    rooms.get_one_for_update.assert_awaited_once_with(id=10)


async def test_add_booking_invalid_dates_never_touches_database():
    db = SimpleNamespace(
        rooms=SimpleNamespace(get_one_for_update=AsyncMock()),
        bookings=SimpleNamespace(add_booking=AsyncMock()),
        commit=AsyncMock(),
    )
    data = BookingAddRequest(room_id=10, date_from=date(2027, 1, 3), date_to=date(2027, 1, 1))

    with pytest.raises(CheckInDateLaterThanCheckOutException):
        await BookingService(db).add_booking(user_id=5, booking_data=data)

    db.rooms.get_one_for_update.assert_not_awaited()
    db.bookings.add_booking.assert_not_awaited()
    db.commit.assert_not_awaited()
