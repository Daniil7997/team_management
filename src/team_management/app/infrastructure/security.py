from app.core.security import (
    create_tokens as security_create_tokens,
)
from app.core.security import (
    decode_token as security_decode_token,
)
from app.core.security import (
    hash_password as security_hash_password,
)
from app.core.security import (
    verify_password as security_verify_password,
)
from app.core.security_dto import AccessTokensPayload, Tokens
from app.domain.shared.custom_types import IdType


class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        return security_hash_password(password)

    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool:
        return security_verify_password(
            raw_password=raw_password, hashed_password=hashed_password
        )

    @staticmethod
    def create_tokens(user_id: IdType) -> Tokens:
        return security_create_tokens(user_id)

    @staticmethod
    def decode_token(token: str) -> AccessTokensPayload:
        return security_decode_token(token)
