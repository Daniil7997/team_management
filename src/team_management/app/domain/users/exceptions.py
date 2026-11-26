from app.core.exceptions.base import AppException


class UserNotFoundError(AppException):
    pass


class EmailAlreadyExistsError(AppException):
    pass


class IncorrectEmailOrPasswordError(AppException):
    pass


class InvalidPasswordError(AppException):
    pass
