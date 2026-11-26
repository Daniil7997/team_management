from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.bootstrap.instances import invite_storage, tokens_blacklist
from app.infrastructure.db.connection import async_session_factory
from app.infrastructure.security import SecurityService
from app.infrastructure.storages.blacklist import TokensBlacklist
from app.infrastructure.storages.invite import InviteStore
from app.infrastructure.unit_of_work import UnitOfWork


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory.begin() as session:
        yield session


def get_unit_of_work(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnitOfWork:
    return UnitOfWork(session)


def get_invite_storage() -> InviteStore:
    return invite_storage


def get_tokens_blacklist() -> TokensBlacklist:
    return tokens_blacklist


def get_security_service() -> SecurityService:
    return SecurityService()
