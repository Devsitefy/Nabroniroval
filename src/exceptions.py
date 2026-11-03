class AppException(Exception):
    detail = "Внутренняя ошибка сервера"


class ObjectNotFoundException(AppException):
    detail = "Объект не найден"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Отель не найден"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Номер не найден"


class ImageNotFoundException(ObjectNotFoundException):
    detail = "Изображение не найдено"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


class UserAlreadyExistsException(AppException):
    detail = "Такой пользователь уже существует"

class InvalidTokenException(AppException):
    detail = "Неверный токен"

class InvalidPasswordException(AppException):
    detail = "Неверный пароль"

class CheckInDateLaterThanCheckOutException(AppException):
    detail = "Дата заезда позже даты выезда"


class CheckInDateEqualsCheckOutException(AppException):
    detail = "Дата заезда равна дате выезда"


class RoomNotAvailableException(AppException):
    detail = "Нет свободных номеров на выбранные даты"


class ImageConflictException(AppException):
    detail = "Изображение уже существует"


class ImageNameNotAvailableException(AppException):
    detail = "Имя файла отсутствует"

class RoomHasBookingsException(AppException):
    detail = "Нельзя удалить номер, у которого есть бронирования"

class InvalidUserException(AppException):
    detail = "Некорректный Email"

class InvalidImageException(AppException):
    detail = "Файл не является корректным изображением"


class ImageTooLargeException(AppException):
    detail = "Размер изображения превышает допустимый"
