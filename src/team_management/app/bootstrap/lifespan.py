from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap.instances import invite_storage, tokens_blacklist
from app.infrastructure.exceptions import (
    InviteStorageUnavailableError,
    TokensBlacklistUnavailableError,
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
    try:
        await invite_storage.startup()
        print("INVITE_STORAGE START")
    except InviteStorageUnavailableError:
        print("INVITE_STORAGE FAILED")
        pass
    try:
        await tokens_blacklist.startup()
        print("TOKENS_BLACKLIST START")
    except TokensBlacklistUnavailableError:
        print("TOKENS_BLACKLIST FAILED")
        pass
    try:
        yield
    finally:
        await invite_storage.shutdown()
        await tokens_blacklist.shutdown()
