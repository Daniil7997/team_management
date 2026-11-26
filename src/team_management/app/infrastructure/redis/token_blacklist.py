from typing import cast

from redis.asyncio import Redis
from redis.backoff import ExponentialWithJitterBackoff
from redis.exceptions import RedisError
from redis.retry import Retry

from app.core.config import settings
from app.infrastructure.exceptions import TokensBlacklistUnavailableError


class RedisTokensBlacklist:
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
            raise TokensBlacklistUnavailableError() from exc
        self.redis = redis

    async def close(self) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.aclose()
        except RedisError as exc:
            raise TokensBlacklistUnavailableError() from exc
        finally:
            self.redis = None

    async def clear(self) -> None:
        redis = self.redis
        if redis is None:
            raise TokensBlacklistUnavailableError()
        try:
            await redis.flushdb()
        except RedisError as exc:
            raise TokensBlacklistUnavailableError() from exc

    async def get(self, key: str) -> str | None:
        redis = self.redis
        if redis is None:
            return None
        try:
            return cast(str | None, await redis.get(key))
        except RedisError:
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: int,
    ) -> None:
        redis = self.redis
        if redis is None:
            raise TokensBlacklistUnavailableError()
        try:
            await redis.set(name=key, ex=expire, value=value)
        except RedisError as exc:
            raise TokensBlacklistUnavailableError() from exc
