from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid6

from payments.infrastructure.db.repositories.outbox_repository import OutboxRepository
from payments.infrastructure.tests.factories import create_outbox


@pytest.mark.asyncio
async def test_add_and_get_by_id_returns_outbox(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)
    outbox = create_outbox()

    await repo.add(outbox)
    await db_session.commit()

    saved_outbox = await repo.get_by_id(outbox.id)

    assert saved_outbox == outbox


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_outbox_not_found(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)

    outbox = await repo.get_by_id(uuid6())

    assert outbox is None


@pytest.mark.asyncio
async def test_add_and_get_by_id_returns_published_outbox(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)
    outbox = create_outbox()
    published_at = datetime.now(UTC)
    outbox.mark_published(published_at)

    await repo.add(outbox)
    await db_session.commit()

    saved_outbox = await repo.get_by_id(outbox.id)

    assert saved_outbox == outbox
    assert saved_outbox is not None
    assert saved_outbox.published_at == published_at
