from app.infrastructure.redis.invite_storage import RedisInviteStorage
from app.infrastructure.redis.token_blacklist import RedisTokensBlacklist
from app.infrastructure.storages.blacklist import TokensBlacklist
from app.infrastructure.storages.invite import InviteStore

tokens_blacklist = TokensBlacklist(storage=RedisTokensBlacklist())
invite_storage = InviteStore(storage=RedisInviteStorage())
