from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin

# Register SQLAlchemy models in Base.metadata
import app.infrastructure.db.models  # ruff: ignore[unused-import] F401
from app.admin.authenticate import AdminAuth
from app.admin.register_views import register_admin_views
from app.core.config import settings
from app.infrastructure.db.connection import sync_engine
from app.presentation.api.handlers.register_handlers import (
    register_all_errors_handlers,
)
from app.presentation.api.v1.routers import main_v1_router


def configure_application(application: FastAPI):

    application.add_middleware(
        SessionMiddleware, secret_key=settings.app.PRIVATE_KEY_HEX
    )

    application.include_router(main_v1_router)

    register_all_errors_handlers(app=application)

    admin = Admin(
        sync_engine,
        base_url="/admin",
        title="Admin panel",
        auth_provider=AdminAuth(),
        templates_dir="app/admin/templates",
        secret_key=settings.app.PRIVATE_KEY_HEX,
    )

    register_admin_views(admin)

    admin.mount_to(application)
