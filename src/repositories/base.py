import logging

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update

from src.exceptions import ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    not_found_exception = ObjectNotFoundException
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_filtred(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if not model:
            raise self.not_found_exception
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        stmt = (
            insert(self.model)
            .values([item.model_dump() for item in data])
            .returning(self.model)
        )
        await self.session.execute(stmt)

    async def edit(self, data: BaseModel, **filter_by):
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=True))
        )
        res = await self.session.execute(stmt)
        if res.rowcount == 0:
            raise self.not_found_exception

    async def delete(self, *filter, **filter_by):
        if not filter and not filter_by:
            raise ValueError("Delete requires filters")
        stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        if res.rowcount == 0:
            raise self.not_found_exception
