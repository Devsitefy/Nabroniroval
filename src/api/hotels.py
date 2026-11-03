from datetime import date, timedelta

from fastapi import APIRouter, Body, Query
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, paginationDep

from src.schemas.hotels import Hotel_patch, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels")


@router.get("/{hotel_id}", summary="получение одного отеля")
async def get_hotel(db: DBDep, hotel_id: int):
    hotel = await HotelService(db).get_hotel(hotel_id)
    return {"status": "OK", "data": hotel}

@router.get("", summary="получение всех отелей")
@cache(expire=60, namespace="hotels")
async def get_hotels(
    pagination: paginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Локация отеля"),
    date_from: date = Query(example=f"{date.today()}"),
    date_to: date = Query(example=f"{date.today() + timedelta(days=5)}"),
):
    hotels = await HotelService(db).get_filterd_by_time(
        pagination, title, location, date_from, date_to
    )

    return {"status": "OK", "data": hotels}


@router.post("", summary="добавление отеля")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "отель 666 звезд у котлована",
                    "location": "Сочи, ул. Строительная д.1",
                },
            },
            "2": {
                "summary": "Дубай",
                "value": {
                    "title": "отель 777 звезд в песочнице",
                    "location": "Дубай, ул. Эскортническая д.777",
                },
            },
        }
    ),
):
    hotel = await HotelService(db).create_hotel(hotel_data)
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}", summary="полное изменение отеля")
async def update_hotel(
    db: DBDep,
    hotel_id: int,
    hotel_data: HotelAdd,
):
    await HotelService(db).update_hotel(hotel_id, hotel_data)
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}


@router.patch("/{hotel_id}", summary="Частичное изменение отеля")
async def partial_update_hotel(db: DBDep, hotel_id: int, hotel_data: Hotel_patch):
    await HotelService(db).update_hotel(hotel_id, hotel_data)
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}


@router.delete("/{hotel_id}", summary="удаление отеля")
async def delete_hotel(db: DBDep, hotel_id: int):
    await HotelService(db).delete_hotel(hotel_id)
    await FastAPICache.clear(namespace="hotels")
    return {"status": "OK"}
