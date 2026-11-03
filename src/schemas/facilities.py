from pydantic import BaseModel, ConfigDict


class FacilitiesAdd(BaseModel):
    title: str


class Facilities(FacilitiesAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Rooms_FacilitiesAdd(BaseModel):
    room_id: int
    facility_id: int


class Rooms_Facilities(Rooms_FacilitiesAdd):
    id: int
