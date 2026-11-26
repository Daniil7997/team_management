import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.config import settings
from app.core.security import create_tokens, hash_password
from app.core.security_dto import Tokens
from app.infrastructure.db.models.teams import Teams
from app.infrastructure.db.models.users import Users
from app.infrastructure.storages.invite import InviteStore
from tests.factories import TestRepos


class TestCreateInvite:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_invite(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        invite_storage: InviteStore,
    ):
        response = await async_client.post(
            url=f"{api_prefix}/teams/{team.id}/invites",
            headers={"Authorization": f"Bearer {manager_tokens.access}"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "invite_code" in data
        assert "invite_code_ttl" in data
        response_invite_code = data["invite_code"]
        storage_team_id = await invite_storage.get_team_id_from_invite_code(
            uuid.UUID(response_invite_code)
        )
        assert str(storage_team_id) == str(team.id)
        assert data["invite_code_ttl"] == settings.app.invite_code_ttl

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_invite_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
        team: Teams,
    ):
        response = await async_client.post(
            url=f"{api_prefix}/teams/{team.id}/invites",
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestJoinTeam:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_join_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        team: Teams,
        team_invite_code: str,
        test_repos: TestRepos,
    ):
        user = await test_repos.users.create_user(
            name="Artem",
            email="artem@example.com",
            hashed_password=hash_password(password="MyStrongPass"),
        )

        user_tokens = create_tokens(user_id=user.id)

        check_before_join = await test_repos.teams.get_team_member(
            user_id=user.id, team_id=team.id
        )
        assert check_before_join is None

        response = await async_client.post(
            url=f"{api_prefix}/teams/members",
            json={"invite_code": team_invite_code},
            headers={"Authorization": f"Bearer {user_tokens.access}"},
        )
        assert response.status_code == status.HTTP_200_OK

        check_after_join = await test_repos.teams.get_team_member(
            user_id=user.id, team_id=team.id
        )
        assert check_after_join is not None
        assert check_after_join.user_id == user.id
        assert check_after_join.team_id == team.id


class TestRemoveMember:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_team_member(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        user_member: Users,
        test_repos: TestRepos,
    ):
        check_before_rm = await test_repos.teams.get_team_member(
            user_id=user_member.id, team_id=team.id
        )
        assert check_before_rm is not None
        assert check_before_rm.user_id == user_member.id
        assert check_before_rm.team_id == team.id

        rm_response = await async_client.delete(
            url=f"{api_prefix}/teams/{team.id}/members/{user_member.id}",
            headers={"Authorization": f"Bearer {manager_tokens.access}"},
        )
        assert rm_response.status_code == status.HTTP_200_OK

        check_after_rm = await test_repos.teams.get_team_member(
            user_id=user_member.id, team_id=team.id
        )
        assert check_after_rm is None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_team_member_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
        team: Teams,
        user_member: Users,
        test_repos: TestRepos,
    ):

        check_before_rm = await test_repos.teams.get_team_member(
            user_id=user_member.id, team_id=team.id
        )
        assert check_before_rm is not None
        assert check_before_rm.user_id == user_member.id
        assert check_before_rm.team_id == team.id

        rm_response = await async_client.delete(
            url=f"{api_prefix}/teams/{team.id}/members/{user_member.id}",
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"},
        )
        assert rm_response.status_code == status.HTTP_403_FORBIDDEN
