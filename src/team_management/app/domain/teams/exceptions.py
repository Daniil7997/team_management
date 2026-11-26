from app.core.exceptions.base import AppException


class TeamMembershipRequiredError(AppException):
    pass


class InviteNotFoundError(AppException):
    pass


class TeamMemberNotFoundError(AppException):
    pass


class LowActorRolePrivilegeError(AppException):
    pass


class TeamNameAlreadyExistError(AppException):
    pass
