import uuid

from pydantic import ValidationError

from app.application.contracts.storages_ports import InviteStoreProtocol
from app.application.services.base import BaseService
from app.core.config import settings
from app.domain.shared.custom_types import IdType
from app.domain.shared.exceptions import InvalidDataError
from app.domain.teams.dto import (
    InviteCodeData,
    TeamMembershipSchema,
    UserPermissions,
)
from app.domain.teams.entities import TeamMembershipDraft
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.exceptions import (
    InviteNotFoundError,
    TeamMemberNotFoundError,
)
from app.domain.teams.invites import generate_invite_code


class TeamsService(BaseService):
    async def create_invite(
        self, team_id: IdType, invite_storage: InviteStoreProtocol
    ) -> InviteCodeData:
        invite_code = generate_invite_code()
        invite_code_ttl = settings.app.invite_code_ttl
        await invite_storage.add_invite_code(
            invite_code=invite_code, team_id=str(team_id), ttl=invite_code_ttl
        )
        return InviteCodeData(
            invite_code=str(invite_code), invite_code_ttl=invite_code_ttl
        )

    async def join_team(
        self,
        invite_code: uuid.UUID,
        user_id: IdType,
        invite_storage: InviteStoreProtocol,
    ) -> IdType:
        print("!!!TEAMS SERVICE join_team!!!")
        print(f"TEAMS SERVICE join_team {invite_storage=}")
        str_team_id = await invite_storage.get_team_id_from_invite_code(
            invite_code=invite_code
        )
        print(f"{str_team_id=}")
        if str_team_id is None:
            raise InviteNotFoundError()
        team_id = IdType(str_team_id)
        try:
            team_member_draft = TeamMembershipDraft(
                user_id=user_id, team_id=team_id, team_role=TeamsRoles.member
            )
        except ValidationError as exc:
            raise InvalidDataError() from exc
        async with self.unit_of_work as uow:
            await uow.teams.join_team(team_member_draft)
        return team_id

    async def get_team_membership(
        self,
        team_id: IdType,
    ) -> list[TeamMembershipSchema]:
        async with self.unit_of_work as uow:
            return await uow.teams.get_team_membership(
                team_id=team_id,
            )

    async def remove_team_member(
        self,
        team_id: IdType,
        member_id: IdType,
        actor_permissions: UserPermissions,
    ) -> IdType:
        async with self.unit_of_work as uow:
            member = await uow.teams.get_team_member(
                member_id=member_id, team_id=team_id
            )
            if member is None:
                raise TeamMemberNotFoundError()

            member.check_delete_permission(actor_permissions)
            removed_id = await uow.teams.remove_team_member(
                member_id=member_id, team_id=team_id
            )
            if removed_id is None:
                raise TeamMemberNotFoundError()
            return removed_id
