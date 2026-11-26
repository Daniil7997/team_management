from typing import Protocol

from app.core.security_dto import AccessTokensPayload, Tokens
from app.domain.shared.custom_types import IdType


class SecurityProtocol(Protocol):
    @staticmethod
    def hash_password(password: str) -> str: ...
    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool: ...
    @staticmethod
    def create_tokens(user_id: IdType) -> Tokens: ...
    @staticmethod
    def decode_token(token: str) -> AccessTokensPayload: ...
