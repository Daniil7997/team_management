from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.shared.exceptions import InvalidDataError


def register_shared_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(InvalidDataError)
    async def handle_invalid_data(request: Request, exc: InvalidDataError):
        msg = exc.msg or "Invalid data"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"msg": msg},
        )
