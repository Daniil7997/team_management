from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.users.exceptions import (
    EmailAlreadyExistsError,
    IncorrectEmailOrPasswordError,
    InvalidPasswordError,
    UserNotFoundError,
)


def register_users_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(request: Request, exc: UserNotFoundError):
        msg = exc.msg or "User not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"msg": msg}
        )

    @app.exception_handler(EmailAlreadyExistsError)
    async def handle_email_already_exists(
        request: Request, exc: EmailAlreadyExistsError
    ):
        msg = exc.msg or "Email already exists"
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"msg": msg}
        )

    @app.exception_handler(IncorrectEmailOrPasswordError)
    async def handle_incorrect_email_or_password(
        request: Request, exc: IncorrectEmailOrPasswordError
    ) -> JSONResponse:
        msg = exc.msg or "Incorrect email or password"
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InvalidPasswordError)
    async def handle_invalid_password(
        request: Request, exc: InvalidPasswordError
    ) -> JSONResponse:
        msg = exc.msg or "Invalid password"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"msg": msg},
        )
