from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local", env_file_encoding="utf-8", extra="ignore"
    )


class DatabaseSettings(SharedConfig):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    IS_TEST_DB: bool = False

    @property
    def dsn_psycopg(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def ready_for_test(self) -> bool:
        return bool(self.IS_TEST_DB is True and "test" in self.DB_NAME.lower())


class RedisSettings(SharedConfig):
    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_HOST: str

    @property
    def _base_dsn(self):
        return (
            f"redis://:{self.REDIS_PASSWORD}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}"
        )

    @property
    def dsn_token_blacklist(self) -> str:
        return self._base_dsn + "/0"

    @property
    def dsn_invite_storage(self) -> str:
        return self._base_dsn + "/1"


class ApplicationSettings(SharedConfig):
    PRIVATE_KEY_HEX: str
    hashed_admin_password: str

    @property
    def access_tokens_ttl(self) -> int:
        return 72 * 60 * 60

    @property
    def invite_code_ttl(self) -> int:
        return 72 * 60 * 60


class AggregateSettings:
    def __init__(self) -> None:
        self.db = DatabaseSettings()  # type: ignore[call-arg]
        self.app = ApplicationSettings()  # type: ignore[call-arg]
        self.redis = RedisSettings()  # type: ignore[call-arg]


settings = AggregateSettings()
