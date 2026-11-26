import uuid
from hashlib import sha256

from app.core.config import settings
from app.infrastructure.storages.ports import KeyValueConsumableStorageProtocol


class InviteStore:
    def __init__(self, storage: KeyValueConsumableStorageProtocol):
        self.storage = storage

    async def startup(self) -> None:
        await self.storage.connect()

    async def shutdown(self) -> None:
        await self.storage.close()

    def __create_key(self, key: uuid.UUID) -> str:
        return sha256(key.bytes).hexdigest()

    async def add_invite_code(
        self,
        invite_code: uuid.UUID,
        team_id: str,
        ttl: int = settings.app.invite_code_ttl,
    ) -> None:
        key = self.__create_key(invite_code)
        print(f"ADAPTER KEY in add_invite_code:-->{key}<--")
        await self.storage.set(key=key, value=team_id, expire=ttl)

    async def get_team_id_from_invite_code(
        self, invite_code: uuid.UUID
    ) -> str | None:
        key = self.__create_key(invite_code)
        print(f"ADAPTER KEY in get_team_id:-->{key}<--")
        return await self.storage.getdel(key)
