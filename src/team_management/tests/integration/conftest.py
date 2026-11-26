import uuid
from collections.abc import AsyncGenerator
from datetime import date, timedelta

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncTransaction,
    async_sessionmaker,
    create_async_engine,
)

from app.bootstrap.instances import invite_storage as invite_store
from app.bootstrap.instances import tokens_blacklist as blacklist
from app.core.config import settings
from app.core.security import create_tokens, hash_password
from app.domain.teams.enums import TeamsRoles
from app.domain.teams.invites import generate_invite_code
from app.infrastructure.db.models.tasks import Tasks
from app.infrastructure.db.models.teams import Teams
from app.infrastructure.db.models.users import Users
from app.infrastructure.storages.blacklist import TokensBlacklist
from app.infrastructure.storages.invite import InviteStore
from app.main import application
from app.presentation.dependencies.infrastructure import get_session
from tests.factories import TestRepos


@pytest.fixture(scope="session")
async def async_engine() -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        url=settings.db.dsn_psycopg,
        echo=False,
    )
    return engine


@pytest.fixture(scope="function")
async def test_session(async_engine) -> AsyncGenerator[AsyncSession]:
    async with async_engine.connect() as conn:
        trans: AsyncTransaction = await conn.begin()
        async_session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )
        session = async_session()
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture(scope="function", autouse=True)
async def db_overrides(test_session):

    def override_get_session():
        return test_session

    application.dependency_overrides[get_session] = override_get_session
    yield
    application.dependency_overrides.clear()


@pytest.fixture
def api_prefix():
    return "/api/v1"


@pytest.fixture
async def async_client():
    async with LifespanManager(app=application):
        transport = ASGITransport(app=application)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            yield client


@pytest.fixture(scope="function")
async def test_repos(test_session) -> TestRepos:
    return TestRepos(test_session)


@pytest.fixture(scope="function")
async def user_admin(test_repos: TestRepos):
    password = "admin123"
    hashed_password = hash_password(password)
    user = await test_repos.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanAdmin",
        hashed_password=hashed_password,
        is_admin=True,
    )
    user.password = password
    return user


@pytest.fixture(scope="function")
async def user_no_team(test_repos: TestRepos):
    password = "secret123"
    hashed_password = hash_password(password)
    user = await test_repos.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanNoTeam",
        hashed_password=hashed_password,
    )
    user.password = password
    return user


@pytest.fixture(scope="function")
async def user_member(test_repos: TestRepos, team: Teams):
    password = "secret1password"
    hashed_password = hash_password(password)
    user = await test_repos.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanTeamMember",
        hashed_password=hashed_password,
    )
    await test_repos.teams.join_team(team_id=team.id, user_id=user.id)
    user.password = password
    return user


@pytest.fixture(scope="function")
async def user_manager(team: Teams, test_repos: TestRepos) -> Users:
    user_password = "MyStrongPassword123"
    user = await test_repos.users.create_user(
        name="Ivan",
        email="ivanmanager@gmain.com",
        hashed_password=hash_password(user_password),
    )
    user.password = user_password
    await test_repos.teams.join_team(
        user_id=user.id, team_id=team.id, team_role=TeamsRoles.manager
    )
    return user


@pytest.fixture(scope="function")
def member_tokens(user_member: Users):
    return create_tokens(user_id=user_member.id)


@pytest.fixture(scope="function")
def manager_tokens(user_manager: Users):
    return create_tokens(user_id=user_manager.id)


@pytest.fixture(scope="function")
def admin_tokens(user_admin: Users):
    return create_tokens(user_id=user_admin.id)


@pytest.fixture(scope="function")
def user_no_team_tokens(user_no_team: Users):
    return create_tokens(user_id=user_no_team.id)


@pytest.fixture(scope="function")
async def team(test_repos: TestRepos) -> Teams:
    team = await test_repos.teams.create_team(
        name="SuperTeam",
        description="My large team for developing cool apps",
    )
    return team


@pytest.fixture(scope="function")
async def team_invite_code(team: Teams, invite_storage: InviteStore) -> str:
    invite_code = generate_invite_code()
    await invite_storage.add_invite_code(
        invite_code=invite_code,
        team_id=str(team.id),
    )
    return str(invite_code)


@pytest.fixture(scope="function")
async def task(
    team: Teams, user_manager: Users, test_repos: TestRepos
) -> Tasks:
    due_date = date.today() + timedelta(days=3)
    return await test_repos.tasks.create_task(
        description="test_task",
        due_date=due_date,
        creator_id=user_manager.id,
        team_id=team.id,
    )


@pytest.fixture(scope="session")
def invite_storage() -> InviteStore:
    return invite_store


@pytest.fixture(scope="session")
def tokens_blacklist() -> TokensBlacklist:
    return blacklist
