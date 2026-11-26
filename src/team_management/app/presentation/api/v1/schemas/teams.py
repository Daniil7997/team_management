import uuid

from pydantic import BaseModel

from app.domain.shared.custom_types import IdType
from app.domain.teams.enums import TeamsRoles


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateInviteResponse(BaseModel):
    invite_code: str
    invite_code_ttl: int


class JoinTeamRequest(BaseModel):
    invite_code: uuid.UUID


class GetMembershipResponse(BaseModel):
    id: IdType
    name: str
    email: str
    team_role: TeamsRoles
