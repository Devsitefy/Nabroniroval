import shutil
from pathlib import Path
from typing import BinaryIO
from PIL import Image, UnidentifiedImageError

from src.exceptions import (
    ImageConflictException,
    ImageNameNotAvailableException,
    InvalidImageException,
    ImageTooLargeException,
)
from src.services.base import BaseService
from src.services.validator import ValidatorService
from src.tasks.tasks import resize_image


class ImagesService(BaseService):
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
    async def upload_images(
        self,
        hotel_id: int,
        room_id: int,
        file: BinaryIO,
        filename: str | None,
    ):
        if filename is None:
            raise ImageNameNotAvailableException
        await ValidatorService(self.db)(
            self.db.rooms,
            id=room_id,
            hotel_id=hotel_id,
        )
        image_path = Path("src/static/images") / filename
        if image_path.exists():
            raise ImageConflictException
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.MAX_IMAGE_SIZE:
            raise ImageTooLargeException
        try:
            with Image.open(file) as image:
                if image.format not in self.ALLOWED_IMAGE_FORMATS:
                    raise InvalidImageException
                image.verify()
        except (UnidentifiedImageError, OSError):
            raise InvalidImageException

        finally:
            file.seek(0)
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file, new_file)

        try:
            resize_image.delay(
                room_id,
                str(image_path),
            )
        except Exception:
            image_path.unlink(missing_ok=True)
            raise

    async def delete_image(self, image_id: int):
        image = await ValidatorService(self.db)(
            self.db.images,
            id=image_id,
        )

        await self.db.images.delete(
            source_image=image.source_image
        )
        await self.db.flush()
        source_path = Path(image.source_image)
        paths = [
            source_path,
            source_path.parent / f"1024_{source_path.name}",
            source_path.parent / f"512_{source_path.name}",
            source_path.parent / f"256_{source_path.name}",
        ]

        for path in paths:
            if path.exists():
                path.unlink()

        await self.db.commit()
