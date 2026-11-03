from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm, ImagesOrm, RoomImageOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facilities, Rooms_Facilities
from src.schemas.hotels import Hotel
from src.schemas.images import Image, RoomImage, RoomImages
from src.schemas.rooms import Room, RoomsWithRels
from src.schemas.users import User, UserWithHashedPassword


class HotelDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = Hotel


class RoomDataMapper(DataMapper):
    db_model = RoomsOrm
    schema = Room


class RoomDataWithRelsMapper(DataMapper):
    db_model = RoomsOrm
    schema = RoomsWithRels

    @classmethod
    def map_to_domain_entity(cls, data):
        images_by_source = {}

        for image in data.images:
            images_by_source.setdefault(
                image.source_image,
                {}
            )

            if "256_" in image.image_url:
                images_by_source[image.source_image]["image_256"] = image.image_url

            elif "512_" in image.image_url:
                images_by_source[image.source_image]["image_512"] = image.image_url

            elif "1024_" in image.image_url:
                images_by_source[image.source_image]["image_1024"] = image.image_url

        images = [
            RoomImages(**image_group)
            for image_group in images_by_source.values()
        ]

        return RoomsWithRels(
            id=data.id,
            hotel_id=data.hotel_id,
            title=data.title,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            facilities=[
                Facilities.model_validate(facility)
                for facility in data.facilities
            ],
            images=images,
        )


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class UserWithHashedPasswordDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserWithHashedPassword


class BookingDataMapper(DataMapper):
    db_model = BookingsOrm
    schema = Booking


class FacilitiesDataMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facilities


class RoomsFacilitiesDataMapper(DataMapper):
    db_model = RoomsFacilitiesOrm
    schema = Rooms_Facilities


class ImagesDataMapper(DataMapper):
    db_model = ImagesOrm
    schema = Image


class RoomImagesDataMapper(DataMapper):
    db_model = RoomImageOrm
    schema = RoomImage
