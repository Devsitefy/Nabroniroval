import asyncio
import uuid
from datetime import date

from src.database import async_session_maker
from src.exceptions import RoomNotAvailableException
from src.schemas.bookings import BookingAddRequest
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.services.bookings import BookingService
from src.utils.db_manager import DBManager


async def test_two_simultaneous_bookings_for_last_room_only_one_wins(db):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Race {suffix}", location="Test"))
    await db.commit()
    room = await db.rooms.add(
        RoomAdd(
            hotel_id=hotel.id,
            title=f"Last room {suffix}",
            description=None,
            price=9999,
            quantity=1,
        )
    )
    await db.commit()
    user_id = (await db.users.get_all())[0].id

    booking_data = BookingAddRequest(
        room_id=room.id,
        date_from=date(2027, 4, 1),
        date_to=date(2027, 4, 3),
    )

    async def attempt_booking():
        async with DBManager(session_factory=async_session_maker) as race_db:
            return await BookingService(race_db).add_booking(user_id, booking_data)

    results = await asyncio.gather(attempt_booking(), attempt_booking(), return_exceptions=True)

    successes = [result for result in results if not isinstance(result, Exception)]
    failures = [result for result in results if isinstance(result, Exception)]

    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], RoomNotAvailableException)

    bookings = await db.bookings.get_filtred(room_id=room.id)
    assert len(bookings) == 1
