from datetime import date

from sqlalchemy import select, exists

from src.exceptions import RoomNotAvailableException
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def add_booking(self, booking_data: BookingAdd):
        query = rooms_ids_for_booking(
            date_from=booking_data.date_from,
            date_to=booking_data.date_to,
            room_id=booking_data.room_id,
        )

        result = await self.session.execute(query)
        res = result.scalars().one_or_none()
        if res is None:
            raise RoomNotAvailableException
        return await self.add(booking_data)

    async def exists_by_room_id(self, room_id: int) -> bool:
        stmt = select(
            exists().where(
                BookingsOrm.room_id == room_id
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar()

    async def get_booking_chekin_today(self):
        query = select(BookingsOrm.user_id).where(BookingsOrm.date_from == date.today())
        result = await self.session.execute(query)
        return result.scalars().all()
