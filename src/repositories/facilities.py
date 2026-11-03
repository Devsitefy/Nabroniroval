from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    FacilitiesDataMapper,
    RoomsFacilitiesDataMapper,
)
from src.schemas.facilities import Rooms_FacilitiesAdd


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilitiesDataMapper


class RoomsFacilitiesRepositiry(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = RoomsFacilitiesDataMapper

    async def patch_facility_ids(self, room_data, room_id: int):
        facility_old = await self.get_filtred(room_id=room_id)
        old_ids = {facility.facility_id for facility in facility_old}
        new_ids = set(room_data.facilities_ids)

        ids_to_add = new_ids - old_ids
        ids_to_delete = old_ids - new_ids

        rooms_facilities_data = [
            Rooms_FacilitiesAdd(room_id=room_id, facility_id=f_id)
            for f_id in ids_to_add
        ]
        if ids_to_delete:
            await self.delete(
                RoomsFacilitiesOrm.facility_id.in_(ids_to_delete), room_id=room_id
            )

        if ids_to_add:
            await self.add_bulk(rooms_facilities_data)
