from pydantic import BaseModel

from app.domain.base.entities import BaseDomainEntity
from app.domain.shared.custom_types import IdType
from app.domain.teams.custom_types import TeamDescriptionType, TeamNameType
from app.domain.teams.dto import UserPermissions
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.exceptions import (
    LowActorRolePrivilegeError,
)


class TeamEntity(BaseDomainEntity):
    id: IdType
    name: TeamNameType
    description: TeamDescriptionType


class TeamDraft(BaseModel):
    name: TeamNameType
    description: TeamDescriptionType


class TeamMembershipEntity(BaseDomainEntity):
    id: IdType
    user_id: IdType
    team_id: IdType
    team_role: TeamsRoles

    def check_delete_permission(self, actor: UserPermissions) -> None:
        """checks whether the actor is allowed to delete"""
        if actor.team_id != self.team_id or actor.team_role <= self.team_role:
            raise LowActorRolePrivilegeError()


class TeamMembershipDraft(BaseModel):
    user_id: IdType
    team_id: IdType
    team_role: TeamsRoles = TeamsRoles.member
