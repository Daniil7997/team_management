from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.teams.exceptions import (
    InviteNotFoundError,
    LowActorRolePrivilegeError,
    TeamMemberNotFoundError,
    TeamMembershipRequiredError,
)


def register_teams_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(TeamMembershipRequiredError)
    async def handle_team_membership_requered(
        reuquest: Request, exc: TeamMembershipRequiredError
    ) -> JSONResponse:
        msg = exc.msg or "User must be a team member"
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"msg": msg}
        )

    @app.exception_handler(InviteNotFoundError)
    async def handle_invite_not_found(
        request: Request, exc: InviteNotFoundError
    ) -> JSONResponse:
        msg = exc.msg or "Invite code not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"msg": msg}
        )

    @app.exception_handler(TeamMemberNotFoundError)
    async def handle_team_member_not_found_member(
        request: Request, exc: TeamMemberNotFoundError
    ):
        msg = exc.msg or ("Team member not found")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"msg": msg}
        )

    @app.exception_handler(LowActorRolePrivilegeError)
    async def handle_low_actor_role_privilege_(
        request: Request, exc: LowActorRolePrivilegeError
    ):
        msg = exc.msg or (
            "You do not have sufficient permissions for this action."
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"msg": msg}
        )
