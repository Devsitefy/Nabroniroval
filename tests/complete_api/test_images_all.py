import io
import uuid
from pathlib import Path
from PIL import Image

from src.schemas.hotels import HotelAdd
from src.schemas.images import ImageAdd
from src.schemas.rooms import RoomAdd


async def _seed_room(db):
    suffix = uuid.uuid4().hex[:8]
    hotel = await db.hotels.add(HotelAdd(title=f"Image Hotel {suffix}", location="Test"))
    await db.commit()
    room = await db.rooms.add(
        RoomAdd(hotel_id=hotel.id, title=f"Image Room {suffix}", description=None, price=1000, quantity=1)
    )
    await db.commit()
    return hotel, room


def make_test_image() -> io.BytesIO:
    file = io.BytesIO()

    Image.new(
        "RGB",
        (100, 100),
    ).save(file, format="PNG")

    file.seek(0)
    return file

async def test_upload_image(ac, db, monkeypatch):
    hotel, room = await _seed_room(db)
    filename = f"test-{uuid.uuid4().hex}.png"
    image_path = Path("src/static/images") / filename
    calls = []

    monkeypatch.setattr(
        "src.services.images.resize_image.delay",
        lambda room_id, path: calls.append((room_id, path)),
    )

    try:
        response = await ac.post(
            "/images/",
            params={"hotel_id": hotel.id, "room_id": room.id},
            files={"file": (filename, make_test_image(), "image/png")},
        )
        assert response.status_code == 200
        assert image_path.exists()
        assert calls == [(room.id, str(image_path))]

        duplicate = await ac.post(
            "/images/",
            params={"hotel_id": hotel.id, "room_id": room.id},
            files={"file": (filename, make_test_image(), "image/png")},
        )
        assert duplicate.status_code == 409
    finally:
        if image_path.exists():
            image_path.unlink()


async def test_delete_image(ac, db):
    source = Path("src/static/images") / f"delete-{uuid.uuid4().hex}.png"
    variants = [
        source,
        source.parent / f"1024_{source.name}",
        source.parent / f"512_{source.name}",
        source.parent / f"256_{source.name}",
    ]
    for path in variants:
        path.write_bytes(b"test")

    image = await db.images.add(ImageAdd(image_url=str(variants[-1]), source_image=str(source)))
    await db.commit()

    response = await ac.delete(f"/images/{image.id}")
    assert response.status_code == 200
    assert all(not path.exists() for path in variants)

    missing = await ac.delete(f"/images/{image.id}")
    assert missing.status_code == 404
