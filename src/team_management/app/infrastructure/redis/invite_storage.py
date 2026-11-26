import logging

from redis.asyncio import Redis
from redis.backoff import ExponentialWithJitterBackoff
from redis.exceptions import RedisError
from redis.retry import Retry

from app.core.config import settings
from app.infrastructure.exceptions import (
    InviteStorageNotConnectedError,
    InviteStorageUnavailableError,
)

log = logging.getLogger("redis_invite_storage")


class RedisInviteStorage:
    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        if self.redis is not None:
            return
        redis = Redis.from_url(
            settings.redis.dsn_token_blacklist,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
            health_check_interval=30,
            retry=Retry(
                ExponentialWithJitterBackoff(cap=2, base=0.1), retries=3
            ),
        )
        try:
            await redis.ping()
        except RedisError as exc:
            raise InviteStorageUnavailableError() from exc
        self.redis = redis

    def _get_client(self):
        if self.redis is None:
            raise InviteStorageNotConnectedError()
        return self.redis

    async def close(self) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.aclose()
        finally:
            self.redis = None

    async def getdel(self, key: str) -> str | None:
        print("INVITE_STORAGE_REDIS")
        print("====getdel====")
        print(f"{key=}")
        print("====getdel====")
        redis = self._get_client()
        try:
            result = await redis.getdel(key)
        except RedisError as exc:
            raise InviteStorageUnavailableError() from exc
        return result

    async def set(
        self,
        key: str,
        value: str,
        expire: int,
    ) -> None:
        print("INVITE_STORAGE_REDIS")
        print("====set====")
        print(f"{key=}")
        print("====set====")
        redis = self._get_client()
        try:
            await redis.set(name=key, value=value, ex=expire)
        except RedisError as exc:
            raise InviteStorageUnavailableError() from exc
