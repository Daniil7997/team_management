from typing import Any

from starlette.requests import Request
from starlette_admin import (
    DateTimeField,
    EnumField,
    HasMany,
    HasOne,
    StringField,
)

from app.admin.base import BaseSQLAView
from app.domain.teams.enums import TeamsRoles
from app.infrastructure.db.models.teams import TeamMembership, Teams


class TeamsView(BaseSQLAView):
    fields = (
        StringField("id", read_only=True),
        StringField("name"),
        StringField("description"),
        DateTimeField("created_at", read_only=True),
        DateTimeField("updated_at", read_only=True),
        HasMany("membership", key="team_membership"),
    )
    relationship_fields = ("membership",)
    searchable_fields = ("id", "name", "description")
    exclude_fields_from_create = (
        *relationship_fields,
        "created_at",
        "updated_at",
    )
    exclude_fields_from_edit = (*relationship_fields,)

    async def repr(self, obj: Teams, request: Request):
        return f"{obj.name}"


class TeamMembershipView(BaseSQLAView):
    fields = (
        StringField("id", read_only=True),
        HasOne("member", key="users"),
        HasOne("team", key="teams"),
        EnumField("team_role", enum=TeamsRoles),
        DateTimeField("created_at", read_only=True),
        DateTimeField("updated_at", read_only=True),
    )
    relationship_fields = (
        "team",
        "member",
    )
    searchable_fields = ("id",)
    exclude_fields_from_edit = (
        *relationship_fields,
        "created_at",
        "updated_at",
    )
    exclude_fields_from_create = (
        *relationship_fields,
        "created_at",
        "updated_at",
    )
    form_autocomplete_fields = (*relationship_fields,)

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        data["user_id"] = data.pop("member")
        data["team_id"] = data.pop("team")
        return await super().create(request, data)

    async def repr(self, obj: TeamMembership, request: Request):
        key = request.path_params["key"]
        if key == "users":
            return f"Team: {obj.team.name}, Role: {obj.team_role}"
        elif key == "teams":
            return f"{obj.member.name} {obj.member.email}"
