import datetime as dt
import typing
from collections.abc import Sequence

from sqlalchemy import Delete, Select, Update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.custom_types import IdType
from app.domain.teams.enums import TeamsRoles
from app.infrastructure.db.models.tasks import Tasks
from app.infrastructure.db.models.teams import TeamMembership, Teams
from app.infrastructure.db.models.users import Users

T_Stmt = typing.TypeVar("T_Stmt", Select, Update, Delete)


class BaseTestRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


class UsersTestRepo(BaseTestRepo):
    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
        is_admin: bool = False,
    ) -> Users:
        user = Users(
            name=name, email=email, password=hashed_password, is_admin=is_admin
        )
        self.session.add(user)
        await self.session.flush()
        self.session.expunge(user)
        return user

    async def get_user(self, user_id: IdType) -> Users | None:
        stmt = select(Users).where(Users.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TeamsTestRepo(BaseTestRepo):
    async def create_team(
        self, name: str, description: str | None = None
    ) -> Teams:
        team = Teams(name=name, description=description)
        self.session.add(team)
        await self.session.flush()
        self.session.expunge(team)
        return team

    async def join_team(
        self,
        team_id: IdType,
        user_id: IdType,
        team_role: TeamsRoles = TeamsRoles.member,
    ) -> None:
        new_member = TeamMembership(
            team_id=team_id, user_id=user_id, team_role=team_role
        )
        self.session.add(new_member)
        await self.session.flush()
        self.session.expunge(new_member)

    async def get_team_member(
        self, user_id: IdType, team_id: IdType
    ) -> TeamMembership | None:
        stmt = select(TeamMembership).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
        )
        return await self.session.scalar(stmt)


class TasksTestRepo(BaseTestRepo):
    async def create_task(
        self,
        description: str,
        due_date: dt.date,
        creator_id: IdType,
        team_id: IdType,
    ) -> Tasks:
        task = Tasks(
            description=description,
            creator_id=creator_id,
            team_id=team_id,
            due_date=due_date,
        )
        self.session.add(task)
        await self.session.flush()
        self.session.expunge(task)
        return task

    async def get_task(self, task_id: IdType) -> Tasks | None:
        stmt = select(Tasks).where(Tasks.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_team_tasks(self, team_id: IdType) -> Sequence[Tasks]:
        stmt = select(Tasks).where(Tasks.team_id == team_id)
        result = await self.session.scalars(stmt)
        return result.all()


class TestRepos:
    __test__ = False

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UsersTestRepo(session)
        self.teams = TeamsTestRepo(session)
        self.tasks = TasksTestRepo(session)
