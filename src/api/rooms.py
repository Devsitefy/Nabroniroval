from datetime import date

from fastapi import APIRouter, Body
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.rooms import Room_patchRequest, RoomAddRequest
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels")


@router.get("/{hotel_id}/rooms", summary="получение всех номеров")
@cache(expire=60, namespace="rooms")
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date,
    date_to: date,
):
    return await RoomService(db).get_rooms(hotel_id, date_from, date_to)

@router.get("/{hotel_id}/rooms/{room_id}", summary="получение одного номера")
async def get_room(db: DBDep, hotel_id: int, room_id: int):
    return await RoomService(db).get_room(hotel_id, room_id)


@router.post("/{hotel_id}/rooms", summary="добавление одного номера")
async def add_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Президентский люкс",
                "value": {
                    "title": "Президентский люкс для непрезидентов",
                    "description": "Огромная комната с видом на соседнюю стену и ощущением успеха",
                    "price": 15000,
                    "quantity": 2,
                },
            },
        }
    ),
):
    room = await RoomService(db).create_room(hotel_id, room_data)
    await FastAPICache.clear(namespace="rooms")
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="полное изменение номера")
async def update_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomAddRequest,
):
    await RoomService(db).update_room(hotel_id, room_id, room_data)
    await FastAPICache.clear(namespace="rooms")
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}", summary="Частичное изменение номера")
async def partial_update_room(
    db: DBDep,
    room_id: int,
    hotel_id: int,
    room_data: Room_patchRequest,
):
    await RoomService(db).partial_update_room(hotel_id, room_id, room_data)
    await FastAPICache.clear(namespace="rooms")
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}", summary="удаление номера")
async def delete_room(db: DBDep, room_id: int, hotel_id: int):
    await RoomService(db).delete_room(room_id, hotel_id)
    await FastAPICache.clear(namespace="rooms")
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}
