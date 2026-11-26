from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.application.contracts.storages_ports import InviteStoreProtocol
from app.application.services.teams import TeamsService
from app.domain.shared.custom_types import IdType
from app.domain.teams.dto import UserPermissions
from app.presentation.api.v1.schemas.common import SuccessMessageResponse
from app.presentation.api.v1.schemas.teams import (
    CreateInviteResponse,
    GetMembershipResponse,
    JoinTeamRequest,
)
from app.presentation.dependencies.auth import (
    id_from_access_token,
    required_manager_or_higher,
    required_member_or_higher,
)
from app.presentation.dependencies.infrastructure import get_invite_storage
from app.presentation.dependencies.teams import teams_service

router = APIRouter(tags=["teams"])


@router.post(
    "/teams/{team_id}/invites",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateInviteResponse,
)
async def create_invite_code(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_manager_or_higher)
    ],
    team_id: Annotated[IdType, Path],
    service: Annotated[TeamsService, Depends(teams_service)],
    invite_storage: Annotated[
        InviteStoreProtocol, Depends(get_invite_storage)
    ],
) -> CreateInviteResponse:
    invite_data = await service.create_invite(
        team_id=team_id, invite_storage=invite_storage
    )
    return CreateInviteResponse(
        invite_code=invite_data.invite_code,
        invite_code_ttl=invite_data.invite_code_ttl,
    )


@router.post(
    "/teams/members",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessageResponse,
)
async def join_team(
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    data: Annotated[JoinTeamRequest, Body()],
    service: Annotated[TeamsService, Depends(teams_service)],
    invite_storage: Annotated[
        InviteStoreProtocol, Depends(get_invite_storage)
    ],
) -> SuccessMessageResponse:
    team_id = await service.join_team(
        user_id=actor_id,
        invite_code=data.invite_code,
        invite_storage=invite_storage,
    )
    msg = f"You have successfully joined team ID {team_id}."
    return SuccessMessageResponse(msg=msg)


@router.get(
    "/teams/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=list[GetMembershipResponse],
)
async def team_members(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_member_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    service: Annotated[TeamsService, Depends(teams_service)],
) -> list[GetMembershipResponse]:
    users = await service.get_team_membership(team_id)
    response = [GetMembershipResponse.model_validate(user) for user in users]
    return response


@router.delete(
    "/teams/{team_id}/members/{member_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessMessageResponse,
)
async def remove_team_member(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_manager_or_higher)
    ],
    member_id: Annotated[IdType, Path()],
    team_id: Annotated[IdType, Path()],
    service: Annotated[TeamsService, Depends(teams_service)],
) -> SuccessMessageResponse:
    removed_member_id = await service.remove_team_member(
        member_id=member_id,
        team_id=team_id,
        actor_permissions=actor_permissions,
    )
    msg = f"Team member with ID {removed_member_id} successfully removed."
    return SuccessMessageResponse(msg=msg)
