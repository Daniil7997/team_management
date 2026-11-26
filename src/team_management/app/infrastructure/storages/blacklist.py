from app.infrastructure.storages.ports import KeyValueReadableStorageProtocol


class TokensBlacklist:
    def __init__(self, storage: KeyValueReadableStorageProtocol):
        self.storage = storage

    async def startup(self) -> None:
        await self.storage.connect()

    async def shutdown(self) -> None:
        await self.storage.close()

    async def get(self, token: str) -> str | None:
        return await self.storage.get(token)

    async def set(self, token: str, user_id: str, ttl: int) -> None:
        await self.storage.set(key=token, value=user_id, expire=ttl)
