from typing import Any

from starlette.requests import Request
from starlette_admin import (
    DateField,
    DateTimeField,
    EnumField,
    HasOne,
    StringField,
)

from app.admin.base import BaseSQLAView
from app.domain.tasks.enums import TaskStatus
from app.infrastructure.db.models.tasks import Tasks


class TasksView(BaseSQLAView):
    fields = (
        StringField("id", read_only=True),
        StringField("description"),
        EnumField("status", enum=TaskStatus),
        DateField("due_date"),
        StringField("verification_url"),
        DateTimeField("created_at", read_only=True),
        DateTimeField("updated_at", read_only=True),
        HasOne("creator", key="users"),
        HasOne("assignee", key="users"),
        HasOne("team", key="teams"),
    )
    relationship_fields = ("creator", "assignee", "team")
    searchable_fields = (*relationship_fields, "id", "description", "status")
    exclude_fields_from_create = (
        "created_at",
        "updated_at",
        "verification_url",
    )
    exclude_fields_from_edit = (
        *relationship_fields,
        "created_at",
        "updated_at",
    )
    form_autocomplete_fields = (*relationship_fields,)

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        creator = data.get("creator")
        assignee = data.get("assignee")
        if creator is not None:
            data["creator_id"] = data.pop("creator")
        if assignee is not None:
            data["assignee_id"] = data.pop("assignee")
        data["team_id"] = data.pop("team")
        return await super().create(request, data)

    async def repr(self, obj: Tasks, request: Request):
        return f"{obj.description} {obj.status}"
