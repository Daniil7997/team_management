from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette_admin.auth import AdminUser, AuthProvider

from app.core.security import verify_password
from app.domain.users.entities import UserEntity
from app.domain.users.exceptions import IncorrectEmailOrPasswordError
from app.infrastructure.db.connection import sync_session_factory
from app.infrastructure.db.models.users import Users


class AdminAuth(AuthProvider):
    async def login(
        self, username: str, password: str, remember_me: bool, request: Request
    ) -> None:
        email = username
        user = self.__get_user(email)
        if user is None:
            raise IncorrectEmailOrPasswordError()
        passwords_match = verify_password(
            raw_password=password, hashed_password=user.password
        )
        if not passwords_match:
            raise IncorrectEmailOrPasswordError()
        request.session.update({"user_email": user.email})

    async def authenticate(self, request: Request) -> AdminUser | None:
        email = request.session.get("user_email")
        if not email:
            return None
        user = self.__get_user(email)
        if user is None:
            return None
        if user.is_admin:
            return AdminUser(username=user.name)

    async def logout(self, request: Request) -> None:
        request.session.clear()

    def __get_user(self, email: str) -> UserEntity | None:
        with sync_session_factory() as session:
            session: Session
            res = session.execute(select(Users).where(Users.email == email))
            user = res.scalar_one_or_none()
        if user is None:
            return None
        return UserEntity.model_validate(user)
