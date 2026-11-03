from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.facilities import FacilitiesOrm


class RoomsOrm(Base):
    __tablename__ = "rooms"

    __table_args__ = (
        CheckConstraint(
            "price > 0",
            name="ck_rooms_price_positive",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_rooms_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities",
    )
    images: Mapped[list["ImagesOrm"]] = relationship(
        secondary="room_images",
        back_populates="rooms",
    )


class ImagesOrm(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str]

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        secondary="room_images",
        back_populates="images",
    )
    source_image: Mapped[str]



class RoomImageOrm(Base):
    __tablename__ = "room_images"
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "image_id",
            name="uq_room_image",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE",))

    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE",))
