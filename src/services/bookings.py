from fastapi_cache import FastAPICache

from src.schemas.bookings import BookingAdd, BookingAddRequest
from src.services.base import BaseService
from src.services.validator import ValidatorService


class BookingService(BaseService):
    async def get_bookings_me(self, user_id: int):
        return await self.db.bookings.get_filtred(user_id=user_id)

    async def get_bookings(self):
        return await self.db.bookings.get_filtred()

    async def add_booking(
        self,
        user_id: int,
        booking_data: BookingAddRequest,
    ):
        ValidatorService.date_validate(booking_data.date_from, booking_data.date_to)
        room = await self.db.rooms.get_one_for_update(id=booking_data.room_id)
        _booking_data = BookingAdd(
            user_id=user_id,
            price=room.price,
            **booking_data.model_dump(),
        )

        booking = await self.db.bookings.add_booking(_booking_data)

        await self.db.commit()
        await FastAPICache.clear(namespace="rooms")
        await FastAPICache.clear(namespace="hotels")
        return booking
