from datetime import date, timedelta

import pytest

from src.exceptions import ObjectNotFoundException
from src.schemas.bookings import BookingAdd, BookingEdit


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room = (await db.rooms.get_all())[1]

    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room.id,
        price=room.price,
        date_from=date.today(),
        date_to=date.today() + timedelta(days=5),
    )

    new_booking_data = await db.bookings.add_booking(booking_data)
    await db.commit()

    last_booking_data = await db.bookings.get_one_or_none(id=new_booking_data.id)

    assert last_booking_data == new_booking_data

    booking_data_update = BookingEdit(
        date_from=date.today() + timedelta(days=1),
    )

    await db.bookings.edit(booking_data_update, id=new_booking_data.id)
    await db.commit()

    updated_booking_data = await db.bookings.get_one_or_none(id=new_booking_data.id)

    assert updated_booking_data.date_from == booking_data_update.date_from

    await db.bookings.delete(id=new_booking_data.id)
    await db.commit()

    with pytest.raises(ObjectNotFoundException):
        await db.bookings.get_one(id=new_booking_data.id)
