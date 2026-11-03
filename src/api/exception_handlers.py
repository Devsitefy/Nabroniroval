from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import (
    AppException,
    HotelNotFoundException,
    RoomNotFoundException,
    ImageNotFoundException,
    UserNotFoundException,
    UserAlreadyExistsException,
    CheckInDateLaterThanCheckOutException,
    CheckInDateEqualsCheckOutException,
    RoomNotAvailableException,
    ImageConflictException,
    ImageNameNotAvailableException,
    InvalidTokenException,
    InvalidPasswordException, RoomHasBookingsException, InvalidUserException, InvalidImageException,
    ImageTooLargeException,
)


EXCEPTION_STATUS_CODES = {
    HotelNotFoundException: status.HTTP_404_NOT_FOUND,
    RoomNotFoundException: status.HTTP_404_NOT_FOUND,
    ImageNotFoundException: status.HTTP_404_NOT_FOUND,
    UserNotFoundException: status.HTTP_404_NOT_FOUND,

    UserAlreadyExistsException: status.HTTP_409_CONFLICT,
    RoomNotAvailableException: status.HTTP_409_CONFLICT,
    ImageConflictException: status.HTTP_409_CONFLICT,
    RoomHasBookingsException: status.HTTP_409_CONFLICT,

    InvalidTokenException: status.HTTP_401_UNAUTHORIZED,
    InvalidPasswordException: status.HTTP_401_UNAUTHORIZED,
    InvalidUserException: status.HTTP_401_UNAUTHORIZED,

    CheckInDateLaterThanCheckOutException: status.HTTP_400_BAD_REQUEST,
    CheckInDateEqualsCheckOutException: status.HTTP_400_BAD_REQUEST,
    ImageNameNotAvailableException: status.HTTP_400_BAD_REQUEST,
    InvalidImageException: status.HTTP_400_BAD_REQUEST,

    ImageTooLargeException: status.HTTP_413_CONTENT_TOO_LARGE,


}


async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    status_code = EXCEPTION_STATUS_CODES.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
    )