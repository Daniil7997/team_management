import typing

from sqlalchemy import Delete, Select, Update, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.shared.custom_types import IdType
from app.domain.tasks.entities import TaskDraft, TaskEntity
from app.domain.teams.dto import (
    TeamMembershipSchema,
    UserPermissions,
)
from app.domain.teams.entities import (
    TeamDraft,
    TeamEntity,
    TeamMembershipDraft,
    TeamMembershipEntity,
)
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.exceptions import TeamNameAlreadyExistError
from app.domain.users.entities import UserDraft, UserEntity
from app.domain.users.exceptions import EmailAlreadyExistsError
from app.infrastructure.db.codes import DBIntegrityState
from app.infrastructure.db.models.tasks import Tasks
from app.infrastructure.db.models.teams import (
    TeamMembership,
    Teams,
)
from app.infrastructure.db.models.users import Users

T_Stmt = typing.TypeVar("T_Stmt", Select, Update, Delete)


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


class UsersRepo(BaseRepo):
    def _only_active_users(self, stmt: T_Stmt) -> T_Stmt:
        return stmt.where(Users.is_active)

    async def register_user(self, user_draft: UserDraft) -> UserEntity:
        try:
            user = Users(
                name=user_draft.name,
                email=user_draft.email,
                password=user_draft.hashed_password,
            )
            self.session.add(user)
            await self.session.flush()
            return UserEntity.model_validate(user)
        except IntegrityError as exc:
            sqlstate = getattr(exc.orig, "sqlstate", None)
            if sqlstate == DBIntegrityState.UNIQUE_VIOLATION:
                raise EmailAlreadyExistsError() from exc
            else:
                raise

    async def get_user_by_email(
        self, email: str, only_active_users: bool = True
    ) -> UserEntity | None:
        stmt = select(Users).where(Users.email == email)
        if only_active_users:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserEntity.model_validate(user)

    async def get_user_by_id(
        self, id: IdType, only_active_users: bool = True
    ) -> UserEntity | None:
        stmt = select(Users).where(Users.id == id)
        if only_active_users:
            stmt = self._only_active_users(stmt=stmt)
        user = await self.session.scalar(stmt)
        if user is None:
            return None
        return UserEntity.model_validate(user)

    async def update_user_data_by_id(
        self, user: UserEntity
    ) -> UserEntity | None:
        user_id = user.id
        user_data = user.model_dump(
            exclude={"id", "is_admin", "created_at", "updated_at"}
        )
        stmt = update(Users).where(Users.id == user_id).values(user_data)
        stmt = stmt.returning(Users)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            return None
        return UserEntity.model_validate(db_user)

    async def check_is_admin(self, user_id: IdType) -> bool | None:
        stmt = select(Users.is_admin).where(Users.id == user_id)
        is_admin = await self.session.scalar(stmt)
        return is_admin


class TeamsRepo(BaseRepo):
    def _only_active_users(self, stmt: T_Stmt) -> T_Stmt:
        return stmt.where(TeamMembership.member.has(Users.is_active))

    async def create_team(self, team: TeamDraft) -> TeamEntity:
        try:
            db_team = Teams(name=team.name, description=team.description)
            self.session.add(db_team)
            await self.session.flush()
            return TeamEntity.model_validate(db_team)
        except IntegrityError as exc:
            sqlstate = getattr(exc.orig, "sqlstate", None)
            if sqlstate == DBIntegrityState.UNIQUE_VIOLATION:
                raise TeamNameAlreadyExistError() from exc
            else:
                raise

    async def change_team_role(
        self, team_id: IdType, member_id: IdType, new_role: str
    ) -> IdType | None:
        stmt = (
            update(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == member_id,
            )
            .values(team_role=new_role)
            .returning(TeamMembership.id)
        )
        return await self.session.scalar(stmt)

    async def join_team(self, team_member: TeamMembershipDraft) -> None:
        member = TeamMembership(
            team_id=team_member.team_id,
            user_id=team_member.user_id,
            team_role=team_member.team_role,
        )
        self.session.add(member)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            sqlstate = getattr(exc.orig, "sqlstate", None)
            if sqlstate == DBIntegrityState.UNIQUE_VIOLATION:
                return
            else:
                raise

    async def get_team_membership(
        self, team_id: IdType, active_members_only: bool = True
    ) -> list[TeamMembershipSchema]:
        stmt = (
            select(
                Users.id,
                Users.name,
                Users.email,
                Users.is_admin,
                TeamMembership.team_role,
            )
            .join_from(
                Users, TeamMembership, TeamMembership.user_id == Users.id
            )
            .where(TeamMembership.team_id == team_id)
        )
        if active_members_only:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.execute(stmt)
        users = result.mappings().all()
        return [TeamMembershipSchema.model_validate(user) for user in users]

    async def get_team_member(
        self,
        team_id: IdType,
        member_id: IdType,
        active_members_only: bool = True,
    ) -> TeamMembershipEntity | None:
        stmt = (
            select(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == member_id,
            )
            .with_for_update()
        )
        if active_members_only:
            stmt = self._only_active_users(stmt=stmt)
        result = await self.session.scalars(stmt)
        member = result.one_or_none()
        if member is None:
            return None
        return TeamMembershipEntity.model_validate(member)

    async def get_team_role(
        self, user_id: IdType, team_id: IdType
    ) -> TeamsRoles | None:
        stmt = select(TeamMembership.team_role).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
        )
        return await self.session.scalar(stmt)

    async def remove_team_member(
        self, team_id: IdType, member_id: IdType
    ) -> IdType | None:
        stmt = (
            delete(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
                TeamMembership.user_id == member_id,
            )
            .returning(TeamMembership.user_id)
        )
        return await self.session.scalar(stmt)

    async def get_permissions(
        self, user_id: IdType, team_id: IdType
    ) -> UserPermissions | None:
        stmt = select(
            TeamMembership.team_role,
            TeamMembership.user_id,
            TeamMembership.team_id,
        ).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
        )
        res = await self.session.execute(stmt)
        row = res.mappings().one_or_none()
        if row is None:
            return None
        return UserPermissions.model_validate(row)


class TasksRepo(BaseRepo):
    async def create_task(self, task: TaskDraft) -> TaskEntity:

        db_task = Tasks(
            description=task.description,
            creator_id=task.creator_id,
            team_id=task.team_id,
            due_date=task.due_date,
            assignee_id=task.assignee_id,
        )
        self.session.add(db_task)
        await self.session.flush()
        return TaskEntity.model_validate(db_task)

    async def update_task(self, task: TaskEntity) -> TaskEntity | None:
        task_id = task.id
        team_id = task.team_id
        task_data = task.model_dump(
            exclude={"id", "team_id", "created_at", "updated_at"}
        )
        stmt = (
            update(Tasks)
            .where(Tasks.id == task_id, Tasks.team_id == team_id)
            .values(task_data)
            .returning(Tasks)
        )
        result = await self.session.execute(stmt)
        updated_task = result.scalar_one_or_none()
        if updated_task is None:
            return None
        return TaskEntity.model_validate(updated_task)

    async def delete_task(
        self, team_id: IdType, task_id: IdType
    ) -> IdType | None:
        stmt = (
            delete(Tasks)
            .where(Tasks.id == task_id, Tasks.team_id == team_id)
            .returning(Tasks.id)
        )
        return await self.session.scalar(stmt)

    async def get_task(
        self, task_id: IdType, team_id: IdType
    ) -> TaskEntity | None:
        stmt = select(Tasks).where(
            Tasks.id == task_id, Tasks.team_id == team_id
        )
        task = await self.session.scalar(stmt)
        if task is None:
            return None
        return TaskEntity.model_validate(task)

    async def get_task_for_update(
        self, task_id: IdType, team_id: IdType
    ) -> TaskEntity | None:
        stmt = (
            select(Tasks)
            .where(Tasks.id == task_id, Tasks.team_id == team_id)
            .with_for_update()
        )
        task = await self.session.scalar(stmt)
        if task is None:
            return None
        return TaskEntity.model_validate(task)
