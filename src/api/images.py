from fastapi import APIRouter, UploadFile

from src.api.dependencies import DBDep

from src.services.images import ImagesService


router = APIRouter(prefix="/images")

@router.post("/")
async def upload_images(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    file: UploadFile,
):
    await ImagesService(db).upload_images(
        room_id=room_id,
        hotel_id=hotel_id,
        file=file.file,
        filename=file.filename,
    )
    return {"status": "OK"}

@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: DBDep,
):
    await ImagesService(db).delete_image(image_id)
    return {"status": "OK"}