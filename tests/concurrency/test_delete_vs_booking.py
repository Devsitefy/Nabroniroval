import asyncio
import uuid
from datetime import date

from src.database import async_session_maker
from src.exceptions import RoomHasBookingsException, RoomNotFoundException
from src.schemas.bookings import BookingAddRequest
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.services.bookings import BookingService
from src.services.rooms import RoomService
from src.utils.db_manager import DBManager


async def test_delete_and_booking_cannot_both_succeed(db):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Delete race {suffix}", location="Test"))
    await db.commit()
    room = await db.rooms.add(
        RoomAdd(
            hotel_id=hotel.id,
            title=f"Delete race room {suffix}",
            description=None,
            price=3000,
            quantity=1,
        )
    )
    await db.commit()
    user_id = (await db.users.get_all())[0].id
    booking_data = BookingAddRequest(
        room_id=room.id,
        date_from=date(2027, 5, 1),
        date_to=date(2027, 5, 3),
    )

    async def book():
        async with DBManager(session_factory=async_session_maker) as race_db:
            return await BookingService(race_db).add_booking(user_id, booking_data)

    async def delete():
        async with DBManager(session_factory=async_session_maker) as race_db:
            return await RoomService(race_db).delete_room(room.id, hotel.id)

    results = await asyncio.gather(book(), delete(), return_exceptions=True)

    # Допустимы два корректных порядка сериализации:
    # booking первым -> delete получает RoomHasBookingsException;
    # delete первым -> booking получает RoomNotFoundException.
    errors = [result for result in results if isinstance(result, Exception)]
    assert len(errors) == 1
    assert isinstance(errors[0], (RoomHasBookingsException, RoomNotFoundException))
