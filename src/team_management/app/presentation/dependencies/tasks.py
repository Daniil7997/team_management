from typing import Annotated

from fastapi import Depends

from app.application.services.tasks import TasksService
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.dependencies.infrastructure import get_unit_of_work


def tasks_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> TasksService:
    return TasksService(unit_of_work=unit_of_work)
