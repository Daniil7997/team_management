import datetime as dt

from pydantic import ValidationError

from app.application.services.base import BaseService
from app.domain.shared.custom_types import IdType
from app.domain.shared.exceptions import InvalidDataError
from app.domain.tasks.entities import TaskDraft, TaskEntity
from app.domain.tasks.enums import TaskStatus
from app.domain.tasks.exceptions import TaskNotFoundError
from app.domain.teams.dto import UserPermissions


class TasksService(BaseService):
    async def create_task(
        self,
        task_description: str,
        task_due_date: dt.date,
        team_id: IdType,
        creator_id: IdType,
    ) -> TaskEntity:
        try:
            task_draft = TaskDraft(
                description=task_description,
                due_date=task_due_date,
                team_id=team_id,
                creator_id=creator_id,
            )
        except ValidationError as exc:
            raise InvalidDataError() from exc
        async with self.unit_of_work as uow:
            task = await uow.tasks.create_task(task_draft)
        return task

    async def update_task(
        self,
        task_description: str,
        task_due_date: dt.date,
        team_id: IdType,
        task_id: IdType,
        actor_permissions: UserPermissions,
    ) -> TaskEntity:
        async with self.unit_of_work as uow:
            task = await uow.tasks.get_task_for_update(
                team_id=team_id, task_id=task_id
            )
            if task is None:
                raise TaskNotFoundError()
            updated_task = task.update_fields(
                description=task_description,
                due_date=task_due_date,
                actor_permissions=actor_permissions,
            )
            db_task = await uow.tasks.update_task(updated_task)
        return db_task

    async def delete_task_by_id(
        self, team_id: IdType, task_id: IdType
    ) -> IdType:
        async with self.unit_of_work as uow:
            deleted_id = await uow.tasks.delete_task(
                task_id=task_id, team_id=team_id
            )
            if deleted_id is None:
                raise TaskNotFoundError()
        return deleted_id

    async def get_task(self, task_id: IdType, team_id: IdType) -> TaskEntity:
        async with self.unit_of_work as uow:
            task = await uow.tasks.get_task(task_id=task_id, team_id=team_id)
            if task is None:
                raise TaskNotFoundError()
        return task

    async def update_task_status(
        self,
        new_status: TaskStatus,
        team_id: IdType,
        task_id: IdType,
        actor_permissions: UserPermissions,
    ) -> TaskEntity:
        async with self.unit_of_work as uow:
            task = await uow.tasks.get_task_for_update(
                task_id=task_id, team_id=team_id
            )
            if task is None:
                raise TaskNotFoundError()
            updated_task = task.change_status(
                new_status=new_status, actor_permissions=actor_permissions
            )
            new_task_data = await uow.tasks.update_task(updated_task)
        return new_task_data
