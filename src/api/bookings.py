from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings")


@router.get("/me")
async def get_bookings_me(
    user_id: UserIdDep,
    db: DBDep,
):
    return await BookingService(db).get_bookings_me(user_id)


@router.get("")
async def get_bookings(
    db: DBDep,
):
    return await BookingService(db).get_bookings()


@router.post("")
async def add_booking(
    user_id: UserIdDep,
    db: DBDep,
    booking_data: BookingAddRequest,
):
    booking = await BookingService(db).add_booking(user_id, booking_data)
    return {"status": "OK", "data": booking}
