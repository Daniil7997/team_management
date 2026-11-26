from typing import Annotated

from pydantic import EmailStr, Field, TypeAdapter

UserNameType = Annotated[str, Field(max_length=50)]
PasswordType = Annotated[str, Field(max_length=30)]
EmailType = Annotated[EmailStr, Field(max_length=50)]

password_adapter = TypeAdapter(PasswordType)
