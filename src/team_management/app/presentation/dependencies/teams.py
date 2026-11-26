from typing import Annotated

from fastapi import Depends

from app.application.services.teams import TeamsService
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.dependencies.infrastructure import get_unit_of_work


def teams_service(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> TeamsService:
    return TeamsService(unit_of_work=unit_of_work)
