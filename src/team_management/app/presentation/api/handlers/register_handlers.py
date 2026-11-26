from fastapi import FastAPI

from app.presentation.api.handlers.auth import register_auth_errors_handlers
from app.presentation.api.handlers.shared import (
    register_shared_errors_handlers,
)
from app.presentation.api.handlers.tasks import register_tasks_errors_handlers
from app.presentation.api.handlers.teams import register_teams_errors_handlers
from app.presentation.api.handlers.users import register_users_errors_handlers

handlers = [
    register_users_errors_handlers,
    register_auth_errors_handlers,
    register_teams_errors_handlers,
    register_tasks_errors_handlers,
    register_shared_errors_handlers,
]


def register_all_errors_handlers(app: FastAPI) -> None:
    for handler in handlers:
        handler(app)
