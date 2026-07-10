import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def make_alembic_config(database_url: str) -> Config:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_db() -> AsyncGenerator[None]:
    settings = Settings()
    alembic_config = make_alembic_config(settings.test_db_url)

    await asyncio.to_thread(command.downgrade, alembic_config, "base")
    await asyncio.to_thread(command.upgrade, alembic_config, "head")

    yield

    await asyncio.to_thread(command.downgrade, alembic_config, "base")


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(Settings().test_db_url)

    async with engine.connect() as conn:
        trans = await conn.begin()

        async with AsyncSession(bind=conn, join_transaction_mode="create_savepoint") as session:
            yield session

        await trans.rollback()

    await engine.dispose()
