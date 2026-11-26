from pydantic import BaseModel

from app.domain.shared.custom_types import IdType
from app.domain.users.custom_types import EmailType, PasswordType, UserNameType


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class RegisterUserRequest(BaseModel):
    name: UserNameType
    password: PasswordType
    email: EmailType


class RegisterUserResponse(BaseModel):
    id: IdType
    name: UserNameType
    email: EmailType


class TokensRequest(BaseModel):
    password: PasswordType
    email: EmailType


class TokensResponse(BaseModel):
    access: str


class ChangePasswordRequest(BaseModel):
    old_password: PasswordType
    new_password: PasswordType
