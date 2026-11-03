import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.api.auth import router as auth_router
from src.api.bookings import router as bookings_router
from src.api.facilities import router as facilities_router
from src.api.hotels import router as hotels_router
from src.api.images import router as images_router
from src.api.rooms import router as rooms_router
from src.init import redis_manager
from src.api.exception_handlers import app_exception_handler
from src.exceptions import AppException

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI Cache initialized")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.include_router(auth_router, tags=["Аутентификация и Авторизация"])
app.include_router(hotels_router, tags=["Отели"])
app.include_router(rooms_router, tags=["Номера"])
app.include_router(bookings_router, tags=["бронирования"])
app.include_router(facilities_router, tags=["Удобства"])
app.include_router(images_router, tags=["Фото Отеля"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, reload_dirs=["src"])
