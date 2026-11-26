from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from app.application.contracts.security_ports import SecurityProtocol
from app.application.contracts.storages_ports import TokensBlacklistProtocol
from app.application.services.auth import AuthService
from app.core.security_dto import AccessTokensPayload
from app.domain.shared.custom_types import IdType
from app.presentation.api.v1.schemas.auth import (
    ChangePasswordRequest,
    RegisterUserRequest,
    RegisterUserResponse,
    TokensRequest,
    TokensResponse,
)
from app.presentation.api.v1.schemas.common import SuccessMessageResponse
from app.presentation.dependencies.auth import (
    auth_service,
    id_from_access_token,
    str_token_from_header,
    verify_access_token,
)
from app.presentation.dependencies.infrastructure import (
    get_security_service,
    get_tokens_blacklist,
)

router = APIRouter(tags=["auth"])


@router.post(
    "/users",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: Annotated[RegisterUserRequest, Body()],
    auth_service: Annotated[AuthService, Depends(auth_service)],
    security_service: Annotated[
        SecurityProtocol, Depends(get_security_service)
    ],
) -> RegisterUserResponse:
    user = await auth_service.register_user(
        name=data.name,
        email=data.email,
        password=data.password,
        security_service=security_service,
    )
    return RegisterUserResponse.model_validate(user.model_dump())


@router.patch(
    "/users/me/password",
    response_model=SuccessMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    data: Annotated[ChangePasswordRequest, Body()],
    id: Annotated[IdType, Depends(id_from_access_token)],
    auth_service: Annotated[AuthService, Depends(auth_service)],
    security_service: Annotated[
        SecurityProtocol, Depends(get_security_service)
    ],
) -> SuccessMessageResponse:
    await auth_service.change_password(
        old_password=data.old_password,
        new_password=data.new_password,
        id=id,
        security_service=security_service,
    )
    return SuccessMessageResponse(msg="Password successfully updated")


@router.post(
    "/tokens", response_model=TokensResponse, status_code=status.HTTP_200_OK
)
async def create_tokens(
    data: Annotated[TokensRequest, Body()],
    auth_service: Annotated[AuthService, Depends(auth_service)],
    security_service: Annotated[
        SecurityProtocol, Depends(get_security_service)
    ],
) -> TokensResponse:
    tokens = await auth_service.get_tokens(
        password=data.password,
        email=data.email,
        security_service=security_service,
    )
    return TokensResponse.model_validate(tokens.model_dump())


@router.post(
    "/logout",
    response_model=SuccessMessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    token: Annotated[str, Depends(str_token_from_header)],
    payload: Annotated[AccessTokensPayload, Depends(verify_access_token)],
    service: Annotated[AuthService, Depends(auth_service)],
    tokens_blacklist: Annotated[
        TokensBlacklistProtocol, Depends(get_tokens_blacklist)
    ],
) -> SuccessMessageResponse:
    await service.logout(
        token=token, payload=payload, tokens_blacklist=tokens_blacklist
    )
    return SuccessMessageResponse(msg="Logout completed successfully")
