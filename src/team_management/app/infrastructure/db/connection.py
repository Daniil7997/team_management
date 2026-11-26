from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

async_engine: AsyncEngine = create_async_engine(url=settings.db.dsn_psycopg)


async_session_factory: async_sessionmaker = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


sync_engine: Engine = create_engine(url=settings.db.dsn_psycopg)


sync_session_factory: sessionmaker = sessionmaker(
    bind=sync_engine, autoflush=False, autocommit=False, expire_on_commit=False
)
