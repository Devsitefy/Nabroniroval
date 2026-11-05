import asyncio
import logging
from pathlib import Path

from PIL import Image


from src.database import async_session_maker_null_pool
from src.schemas.images import ImageAdd, RoomImageAdd
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager
from src.utils.email_sendler import send_email, send_email_chekin_td


async def save_images_to_db(room_id: int, image_paths: list[str], source_image: str):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        for image_path in image_paths:
            image = await db.images.add(
                ImageAdd(image_url=str(image_path), source_image=source_image,)
            )
            await db.room_images.add(
                RoomImageAdd(
                    room_id=room_id,
                    image_id=image.id,
                )
            )

        await db.commit()


@celery_instance.task
def resize_image(room_id: int, image_path: str):

    logging.info(f"Обрабатывается изображение: {image_path}")
    image_path = Path(image_path)
    resized_paths = []

    with Image.open(image_path) as image:
        for width in (1024, 512, 256):
            height = int(image.height * width / image.width)

            resized = image.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

            output_path = image_path.parent / f"{width}_{image_path.name}"
            resized.save(output_path)
            resized_paths.append(str(output_path))
            logging.info(f"Сохранено: {output_path}")

    asyncio.run(
        save_images_to_db(
            room_id=room_id,
            image_paths=resized_paths,
            source_image=str(image_path),
        )
    )


async def get_booking_chekin_today_helper():
    async with DBManager(
        session_factory=async_session_maker_null_pool
    ) as db:
        user_ids = await db.bookings.get_booking_chekin_today()

    for user_id in set(user_ids):
        await send_email_chekin_td(user_id)


@celery_instance.task(name="booking_today_chekin")
def send_email_to_users_with_today_chekin():
    asyncio.run(get_booking_chekin_today_helper())

