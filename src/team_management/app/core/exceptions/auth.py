from app.core.exceptions.base import AppException


class ForbiddenError(AppException):
    pass


class InvalidTokenTypeError(AppException):
    pass


class UnauthorizedError(AppException):
    pass
