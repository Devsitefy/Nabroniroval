from src.exceptions import ImageNotFoundException
from src.models.rooms import ImagesOrm, RoomImageOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import (
    ImagesDataMapper,
    RoomImagesDataMapper,
)


class ImagesRepository(BaseRepository):
    model = ImagesOrm
    mapper = ImagesDataMapper
    not_found_exception = ImageNotFoundException


class RoomImagesRepository(BaseRepository):
    model = RoomImageOrm
    mapper = RoomImagesDataMapper
    not_found_exception = ImageNotFoundException