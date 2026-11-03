from datetime import date

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class BookingsOrm(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "price > 0",
            name="ck_bookings_price_positive",
        ),
        CheckConstraint(
            "date_to > date_from",
            name="ck_bookings_dates_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column()
    date_to: Mapped[date] = mapped_column()
    price: Mapped[int] = mapped_column()

    @hybrid_property
    def total_cost(self) -> int:
        return self.price * (self.date_to - self.date_from).days
