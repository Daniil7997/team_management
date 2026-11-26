import uuid

from pydantic import BaseModel


class AccessTokensPayload(BaseModel):
    sub: uuid.UUID
    iat: int
    exp: int
    token_type: str


class Tokens(BaseModel):
    access: str
