from fastapi import APIRouter

from app.presentation.api.v1.endpoints.auth import router as auth_router
from app.presentation.api.v1.endpoints.tasks import router as tasks_router
from app.presentation.api.v1.endpoints.teams import router as teams_router

routers = [auth_router, teams_router, tasks_router]


main_v1_router = APIRouter(prefix="/api/v1")


for router in routers:
    main_v1_router.include_router(router)
