from datetime import date

from pydantic import BaseModel, ConfigDict


class BookingAddRequest(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class BookingAdd(BaseModel):
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int


class Booking(BookingAdd):
    id: int


class BookingEdit(BaseModel):
    user_id: int | None = None
    room_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    price: int | None = None


class BookingPath(BaseModel):
    user_id: int | None = None
    room_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None

    model_config = ConfigDict(from_attributes=True)
