from datetime import date

from sqlalchemy import select

from src.exceptions import (
    HotelNotFoundException,
)
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import rooms_ids_for_booking, date_validate



class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper
    not_found_exception = HotelNotFoundException

    async def get_filtred_by_time(
        self,
        date_from: date,
        date_to: date,
        limit: int,
        offset: int,
        location: str | None,
        title: str | None,
    ):
        date_validate(date_from, date_to)
        rooms_ids_for_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(
                RoomsOrm.id.in_(rooms_ids_for_get),
            )
        )
        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))
        if location:
            query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
        if title:
            query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return [
            self.mapper.map_to_domain_entity(hotel)
            for hotel in result.unique().scalars().all()
        ]
