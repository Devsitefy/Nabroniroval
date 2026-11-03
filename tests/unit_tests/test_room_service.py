from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.exceptions import RoomHasBookingsException
from src.services.rooms import RoomService


async def test_delete_room_locks_checks_bookings_deletes_and_commits():
    events = []
    rooms = SimpleNamespace(get_one_for_update=AsyncMock(), delete=AsyncMock())
    bookings = SimpleNamespace(exists_by_room_id=AsyncMock())
    db = SimpleNamespace(rooms=rooms, bookings=bookings, commit=AsyncMock())

    async def lock(**kwargs):
        events.append("lock")

    async def exists(room_id):
        events.append("check")
        return False

    async def delete(**kwargs):
        events.append("delete")

    async def commit():
        events.append("commit")

    rooms.get_one_for_update.side_effect = lock
    bookings.exists_by_room_id.side_effect = exists
    rooms.delete.side_effect = delete
    db.commit.side_effect = commit

    await RoomService(db).delete_room(room_id=10, hotel_id=20)

    assert events == ["lock", "check", "delete", "commit"]
    rooms.get_one_for_update.assert_awaited_once_with(id=10, hotel_id=20)


async def test_delete_room_with_bookings_stops_before_delete():
    rooms = SimpleNamespace(get_one_for_update=AsyncMock(), delete=AsyncMock())
    bookings = SimpleNamespace(exists_by_room_id=AsyncMock(return_value=True))
    db = SimpleNamespace(rooms=rooms, bookings=bookings, commit=AsyncMock())

    with pytest.raises(RoomHasBookingsException):
        await RoomService(db).delete_room(room_id=10, hotel_id=20)

    rooms.delete.assert_not_awaited()
    db.commit.assert_not_awaited()
