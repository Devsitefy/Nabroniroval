from src.schemas.facilities import FacilitiesAdd
from src.services.base import BaseService


class FacilityService(BaseService):
    async def add_facilities(self, facilities_data: FacilitiesAdd):
        facilities = await self.db.facilities.add(facilities_data)
        await self.db.commit()
        return facilities

    async def get_facilities(self):
        facilities = await self.db.facilities.get_filtred()
        return facilities
