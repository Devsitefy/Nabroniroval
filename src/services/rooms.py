from datetime import date

from src.exceptions import RoomHasBookingsException
from src.schemas.facilities import Rooms_FacilitiesAdd
from src.schemas.rooms import Room_patch, Room_patchRequest, RoomAdd, RoomAddRequest
from src.services.base import BaseService
from src.services.validator import ValidatorService


class RoomService(BaseService):
    async def get_rooms(self, hotel_id: int, date_from: date, date_to: date):
        return await self.db.rooms.get_filtred_by_time(
            hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, hotel_id: int, room_id: int):
        return await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)

    async def create_room(self, hotel_id, room_data: RoomAddRequest):
        await ValidatorService(self.db)(self.db.hotels, id=hotel_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)
        rooms_facilities_data = [
            Rooms_FacilitiesAdd(room_id=room.id, facility_id=f_id)
            for f_id in room_data.facilities_ids
        ]
        if rooms_facilities_data:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()
        return room

    async def update_room(self, hotel_id: int, room_id: int, room_data: RoomAddRequest):
        await ValidatorService(self.db)(self.db.rooms, id=room_id, hotel_id=hotel_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await self.db.rooms_facilities.patch_facility_ids(room_data, room_id)
        await self.db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data)
        await self.db.commit()

    async def partial_update_room(
        self, hotel_id: int, room_id: int, room_data: Room_patchRequest
    ):
        await ValidatorService(self.db)(self.db.rooms, id=room_id, hotel_id=hotel_id)
        _room_data = Room_patch(
            hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True)
        )

        if room_data.facilities_ids is not None:
            await self.db.rooms_facilities.patch_facility_ids(room_data, room_id)
        await self.db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data)
        await self.db.commit()

    async def delete_room(self, room_id: int, hotel_id: int):
        await self.db.rooms.get_one_for_update(
            id=room_id,
            hotel_id=hotel_id,
        )
        if await self.db.bookings.exists_by_room_id(room_id):
           raise RoomHasBookingsException
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()
