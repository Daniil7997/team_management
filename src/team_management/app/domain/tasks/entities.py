import datetime as dt

from pydantic import BaseModel

from app.domain.base.entities import BaseDomainEntity
from app.domain.shared.custom_types import IdType
from app.domain.tasks.custom_types import TaskDescriptionType
from app.domain.tasks.enums import TaskStatus
from app.domain.tasks.exceptions import TaskNotFoundError
from app.domain.teams.dto import UserPermissions
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.exceptions import LowActorRolePrivilegeError


class TaskEntity(BaseDomainEntity):
    id: IdType
    description: TaskDescriptionType
    due_date: dt.date
    status: TaskStatus
    team_id: IdType
    creator_id: IdType
    verification_url: str | None
    assignee_id: IdType | None

    def change_status(
        self, new_status: TaskStatus, actor_permissions: UserPermissions
    ) -> TaskEntity:
        if actor_permissions.team_id != self.team_id:
            raise TaskNotFoundError()
        if (
            actor_permissions.team_role >= TeamsRoles.manager
            or actor_permissions.user_id == self.assignee_id
        ):
            return self.model_copy(update={"status": new_status})
        raise LowActorRolePrivilegeError()

    def update_fields(
        self,
        description: str,
        due_date: dt.date,
        actor_permissions: UserPermissions,
    ) -> TaskEntity:
        if actor_permissions.team_role < TeamsRoles.manager or str(
            actor_permissions.team_id
        ) != str(self.team_id):
            print("=========DOMAIN=========")
            print(f"actor team_id {actor_permissions.team_id=}")
            print(f"team_id {self.team_id}")
            print(f"actor_team_id str {actor_permissions.team_id!s}")
            print(f"team_id str {self.team_id!s}")
            print(
                "team_role < manager "
                f"{actor_permissions.team_role <= TeamsRoles.manager}"
            )
            print(
                "actor_team_id != team_id "
                f"{actor_permissions.team_id != self.team_id}"
            )
            print("raise LowActorRolePrivilegeError()")
            print("=========DOMAIN=========")
            raise LowActorRolePrivilegeError()
        return self.model_copy(
            update={"description": description, "due_date": due_date}
        )


class TaskDraft(BaseModel):
    description: TaskDescriptionType
    due_date: dt.date
    status: TaskStatus = TaskStatus.open
    team_id: IdType
    creator_id: IdType
    verification_url: str | None = None
    assignee_id: IdType | None = None
