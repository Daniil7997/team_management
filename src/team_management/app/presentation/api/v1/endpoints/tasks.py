from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.application.services.tasks import TasksService
from app.domain.shared.custom_types import IdType
from app.domain.teams.dto import UserPermissions
from app.presentation.api.v1.schemas.common import SuccessMessageResponse
from app.presentation.api.v1.schemas.tasks import (
    ChangeTaskStatusRequest,
    ChangeTaskStatusResponse,
    CreateTaskRequest,
    CreateTaskResponse,
    GetTaskResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
)
from app.presentation.dependencies.auth import (
    id_from_access_token,
    required_manager_or_higher,
    required_member_or_higher,
)
from app.presentation.dependencies.tasks import tasks_service

router = APIRouter(tags=["tasks"])


@router.post(
    "/teams/{team_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTaskResponse,
)
async def create_task(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_manager_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    creator_id: Annotated[IdType, Depends(id_from_access_token)],
    data: Annotated[CreateTaskRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)],
) -> CreateTaskResponse:
    task = await service.create_task(
        task_description=data.description,
        task_due_date=data.due_date,
        creator_id=creator_id,
        team_id=team_id,
    )
    return CreateTaskResponse.model_validate(task.model_dump())


@router.put(
    "/teams/{team_id}/tasks/{task_id}",
    response_model=UpdateTaskResponse,
    status_code=status.HTTP_200_OK,
)
async def update_task_by_id(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_manager_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    data: Annotated[UpdateTaskRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)],
) -> UpdateTaskResponse:
    task = await service.update_task(
        team_id=team_id,
        task_id=task_id,
        task_description=data.description,
        task_due_date=data.due_date,
        actor_permissions=actor_permissions,
    )
    return UpdateTaskResponse.model_validate(task.model_dump())


@router.delete(
    "/teams/{team_id}/tasks/{task_id}",
    response_model=SuccessMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_task_by_id(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_manager_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    service: Annotated[TasksService, Depends(tasks_service)],
) -> SuccessMessageResponse:
    deleted_task_id = await service.delete_task_by_id(
        team_id=team_id, task_id=task_id
    )
    msg = f"Successfully deleted task ID{deleted_task_id}"
    return SuccessMessageResponse(msg=msg)


@router.get(
    "/teams/{team_id}/tasks/{task_id}",
    response_model=GetTaskResponse,
    status_code=status.HTTP_200_OK,
)
async def get_task_by_id(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_member_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    service: Annotated[TasksService, Depends(tasks_service)],
) -> GetTaskResponse:
    task = await service.get_task(team_id=team_id, task_id=task_id)
    return GetTaskResponse.model_validate(task.model_dump())


@router.patch(
    "/teams/{team_id}/tasks/{task_id}",
    response_model=ChangeTaskStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def change_task_status_by_id(
    actor_permissions: Annotated[
        UserPermissions, Depends(required_member_or_higher)
    ],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    data: Annotated[ChangeTaskStatusRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)],
) -> ChangeTaskStatusResponse:
    task = await service.update_task_status(
        team_id=team_id,
        task_id=task_id,
        new_status=data.new_status,
        actor_permissions=actor_permissions,
    )
    return ChangeTaskStatusResponse.model_validate(task.model_dump())
