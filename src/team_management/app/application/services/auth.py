from datetime import UTC, datetime

from pydantic import ValidationError

from app.application.contracts.security_ports import SecurityProtocol
from app.application.contracts.storages_ports import TokensBlacklistProtocol
from app.application.services.base import BaseService
from app.core.security_dto import AccessTokensPayload, Tokens
from app.domain.shared.custom_types import IdType
from app.domain.shared.exceptions import InvalidDataError
from app.domain.users.entities import UserDraft, UserEntity
from app.domain.users.exceptions import (
    IncorrectEmailOrPasswordError,
    UserNotFoundError,
)


class AuthService(BaseService):
    async def register_user(
        self,
        name: str,
        password: str,
        email: str,
        security_service: SecurityProtocol,
    ) -> UserEntity:
        hashed_password = security_service.hash_password(password)
        try:
            user_draft = UserDraft(
                name=name,
                email=email,
                raw_password=password,
                hashed_password=hashed_password,
            )
        except ValidationError as exc:
            raise InvalidDataError() from exc
        async with self.unit_of_work as uow:
            return await uow.users.register_user(user_draft)

    async def get_tokens(
        self, password: str, email: str, security_service: SecurityProtocol
    ) -> Tokens:
        async with self.unit_of_work as uow:
            repo = uow.users
            user = await repo.get_user_by_email(email)
            if user is None:
                raise UserNotFoundError()
            passwords_match = security_service.verify_password(
                raw_password=password, hashed_password=user.password
            )
            if not passwords_match:
                raise IncorrectEmailOrPasswordError()
            return security_service.create_tokens(user_id=user.id)

    async def change_password(
        self,
        old_password: str,
        new_password: str,
        id: IdType,
        security_service: SecurityProtocol,
    ) -> None:
        async with self.unit_of_work as uow:
            repo = uow.users
            user = await repo.get_user_by_id(id=id)
            if user is None:
                raise UserNotFoundError()
            passwords_match = security_service.verify_password(
                hashed_password=user.password, raw_password=old_password
            )
            if not passwords_match:
                raise IncorrectEmailOrPasswordError()
            hashed_new_password = security_service.hash_password(new_password)
            new_user_data = user.change_password(
                new_raw_password=new_password,
                hashed_password=hashed_new_password,
            )
            await repo.update_user_data_by_id(new_user_data)

    async def logout(
        self,
        token: str,
        payload: AccessTokensPayload,
        tokens_blacklist: TokensBlacklistProtocol,
    ) -> None:
        current_time = datetime.now(UTC).timestamp()
        expire = int(payload.exp - current_time)
        if expire <= 0:
            return
        await tokens_blacklist.set(
            token=token, user_id=str(payload.sub), ttl=expire
        )
