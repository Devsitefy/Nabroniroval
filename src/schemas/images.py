from pydantic import BaseModel


class ImageAdd(BaseModel):
    image_url: str
    source_image: str
class Image(ImageAdd):
    id: int

class RoomImageAdd(BaseModel):
    room_id: int
    image_id: int

class RoomImage(RoomImageAdd):
    id: int

class RoomImages(BaseModel):
    image_256: str
    image_512: str
    image_1024: str