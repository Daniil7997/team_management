from pydantic import (
    BaseModel,
    ValidationError,
)

from app.domain.base.entities import BaseDomainEntity
from app.domain.shared.custom_types import IdType
from app.domain.users.custom_types import (
    EmailType,
    PasswordType,
    UserNameType,
    password_adapter,
)
from app.domain.users.exceptions import InvalidPasswordError


class UserEntity(BaseDomainEntity):
    id: IdType
    name: UserNameType
    email: EmailType
    password: str
    is_admin: bool
    is_active: bool

    def __validate_password(self, raw_password: str) -> None:
        try:
            password_adapter.validate_python(raw_password)
        except ValidationError as exc:
            raise InvalidPasswordError() from exc

    def change_password(
        self, new_raw_password: str, hashed_password: str
    ) -> UserEntity:
        self.__validate_password(new_raw_password)
        return self.model_copy(update={"password": hashed_password})


class UserDraft(BaseModel):
    name: UserNameType
    email: EmailType
    raw_password: PasswordType
    hashed_password: str
    is_admin: bool = False
    is_active: bool = True
