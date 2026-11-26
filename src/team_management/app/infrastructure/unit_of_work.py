from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories import (
    TasksRepo,
    TeamsRepo,
    UsersRepo,
)


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.users = UsersRepo(self.session)
        self.teams = TeamsRepo(self.session)
        self.tasks = TasksRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
