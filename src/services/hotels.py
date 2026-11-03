from datetime import date
from src.services.base import BaseService
from src.services.validator import ValidatorService


class HotelService(BaseService):
    async def get_filterd_by_time(
        self,
        pagination,
        title: str | None,
        location: str | None,
        date_from: date,
        date_to: date,
    ):
        per_page = pagination.per_page or 5

        return await self.db.hotels.get_filtred_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: int):
        return await ValidatorService(self.db)(
            self.db.hotels,
            id=hotel_id,
        )

    async def create_hotel(self, hotel_data):
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return hotel

    async def update_hotel(self, hotel_id, hotel_data):
        await self.db.hotels.edit(id=hotel_id, data=hotel_data)
        await self.db.commit()

    async def delete_hotel(self, hotel_id):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
