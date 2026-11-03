from fastapi import APIRouter, Body
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities")


@router.get("", summary="Получение всех удобств")
@cache(expire=60, namespace="facilities")
async def get_facilities(db: DBDep):
    facilities = await FacilityService(db).get_facilities()
    return facilities


@router.post("", summary="Добавление удобств")
async def add_facilities(
    db: DBDep,
    facilities_data: FacilitiesAdd = Body(openapi_examples={
            "1": {"summary": "Кондиционер", "value": {"title": "Кондиционер"}}
        }),):
    facilities = await FacilityService(db).add_facilities(facilities_data)
    await FastAPICache.clear(namespace="facilities")
    return {"status": "OK", "data": facilities}
