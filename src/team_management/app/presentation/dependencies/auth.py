from typing import Annotated

from fastapi import Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.services.auth import AuthService
from app.core.exceptions.auth import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.core.security_dto import AccessTokensPayload
from app.domain.shared.custom_types import IdType
from app.domain.teams.dto import UserPermissions
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.exceptions import TeamMembershipRequiredError
from app.infrastructure.storages.blacklist import TokensBlacklist
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.dependencies.infrastructure import (
    get_tokens_blacklist,
    get_unit_of_work,
)

auth_scheme = HTTPBearer()


def auth_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> AuthService:
    return AuthService(unit_of_work=unit_of_work)


def str_token_from_header(
    token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> str:
    return str(token.credentials)


async def verify_access_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
    tokens_blacklist: Annotated[
        TokensBlacklist, Depends(get_tokens_blacklist)
    ],
) -> AccessTokensPayload:
    blocked = await tokens_blacklist.get(str(token.credentials))
    if blocked:
        raise UnauthorizedError()
    return decode_token(token=token.credentials)


def id_from_access_token(
    payload: Annotated[AccessTokensPayload, Depends(verify_access_token)],
) -> IdType:
    return payload.sub


async def actor_permissions_from_db(
    team_id: Annotated[IdType, Path()],
    user_id: Annotated[IdType, Depends(id_from_access_token)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> UserPermissions:
    async with unit_of_work as uow:
        actor_permissions = await uow.teams.get_permissions(
            user_id=user_id, team_id=team_id
        )
        if actor_permissions is None:
            raise TeamMembershipRequiredError()
        return actor_permissions


def required_manager_or_higher(
    actor_permissions: Annotated[
        UserPermissions, Depends(actor_permissions_from_db)
    ],
) -> UserPermissions:
    access_granted = actor_permissions.team_role >= TeamsRoles.manager
    print(f"{access_granted=}")
    if not access_granted:
        raise ForbiddenError()
    return actor_permissions


def required_member_or_higher(
    actor_permissions: Annotated[
        UserPermissions, Depends(actor_permissions_from_db)
    ],
) -> UserPermissions:
    access_granted = actor_permissions.team_role >= TeamsRoles.member
    if not access_granted:
        raise ForbiddenError()
    return actor_permissions


async def required_admin(
    user_id: Annotated[IdType, Depends(id_from_access_token)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> bool:
    async with unit_of_work as uow:
        is_admin: bool = await uow.users.check_is_admin(user_id=user_id)
        if not is_admin:
            raise ForbiddenError()
    return is_admin
