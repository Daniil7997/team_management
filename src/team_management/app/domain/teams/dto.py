import datetime as dt

from pydantic import BaseModel, ConfigDict

from app.domain.shared.custom_types import IdType
from app.domain.teams.custom_types import TeamDescriptionType, TeamNameType
from app.domain.teams.enums import TeamsRoles


class TeamsSchema(BaseModel):
    id: IdType
    name: TeamNameType
    description: TeamDescriptionType
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMembershipSchema(BaseModel):
    id: IdType
    name: str
    email: str
    team_role: TeamsRoles

    model_config = ConfigDict(from_attributes=True)


class InviteCodeData(BaseModel):
    invite_code: str
    invite_code_ttl: int


class UserPermissions(BaseModel):
    user_id: IdType
    team_id: IdType
    team_role: TeamsRoles
