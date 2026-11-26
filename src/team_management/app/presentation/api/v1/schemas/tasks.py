import datetime as dt

from pydantic import BaseModel

from app.domain.shared.custom_types import IdType
from app.domain.tasks.custom_types import TaskDescriptionType
from app.domain.tasks.enums import TaskStatus


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateTaskRequest(BaseModel):
    description: TaskDescriptionType
    due_date: dt.date


class CreateTaskResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class UpdateTaskRequest(BaseModel):
    description: TaskDescriptionType
    due_date: dt.date


class UpdateTaskResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class GetTaskResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class ChangeTaskStatusRequest(BaseModel):
    new_status: TaskStatus


class ChangeTaskStatusResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None
