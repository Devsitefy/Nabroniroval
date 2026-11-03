from datetime import date

from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from src.exceptions import (
    CheckInDateEqualsCheckOutException,
    CheckInDateLaterThanCheckOutException,
    RoomNotFoundException,
)
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking, date_validate



class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper
    not_found_exception = RoomNotFoundException

    async def get_filtred_by_time(self, hotel_id, date_from: date, date_to: date):
        date_validate(date_from, date_to)
        rooms_ids_for_get = rooms_ids_for_booking(date_from, date_to, hotel_id)
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities), joinedload(self.model.images))
            .filter(RoomsOrm.id.in_(rooms_ids_for_get))
        )
        result = await self.session.execute(query)
        return [
            RoomDataWithRelsMapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]

    async def get_one(self, **filter_by):
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities), joinedload(self.model.images))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        model = result.unique().scalars().one_or_none()
        if not model:
            raise RoomNotFoundException
        return RoomDataWithRelsMapper.map_to_domain_entity(model)

    async def get_one_for_update(self, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .with_for_update()
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            raise RoomNotFoundException
        return model

    async def add_bulk(self, data: list[BaseModel]):
        if not data:
            return

        stmt = (
            insert(self.model)
            .values([item.model_dump() for item in data])
            .returning(self.model)
        )
        await self.session.execute(stmt)
