from typing import Any

from starlette.requests import Request
from starlette_admin import BooleanField, DateTimeField, HasMany, StringField

from app.admin.base import BaseSQLAView
from app.core.security import hash_password


class UsersView(BaseSQLAView):
    fields = (
        StringField("id", read_only=True),
        StringField("name"),
        StringField("email"),
        StringField("password"),
        BooleanField("is_admin", read_only=True),
        BooleanField("is_active"),
        DateTimeField("created_at", read_only=True),
        DateTimeField("updated_at", read_only=True),
        HasMany("membership", key="team_membership", read_only=True),
    )
    relationship_fields = ("membership",)
    searchable_fields = ("id", "name", "email", "is_active")
    exclude_fields_from_create = (
        *relationship_fields,
        "is_admin",
        "is_active",
        "created_at",
        "updated_at",
    )
    exclude_fields_from_edit = (
        *relationship_fields,
        "password",
        "is_admin",
        "created_at",
        "updated_at",
    )
    exclude_fields_from_detail = ("password",)

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        password = data.get("password")
        if password is not None:
            data["password"] = hash_password(password)
        return await super().create(request, data)
