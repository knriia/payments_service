from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid6

from payments.infrastructure.db.repositories.outbox_repository import OutboxRepository
from payments.tests.factories import create_outbox


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


@pytest.mark.asyncio
async def test_list_unpublished_returns_only_unpublished_outbox_records(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)

    unpublished_outbox = create_outbox()
    published_outbox = create_outbox()
    published_outbox.mark_published(datetime.now(UTC))

    await repo.add(unpublished_outbox)
    await repo.add(published_outbox)
    await db_session.commit()

    result = await repo.list_unpublished(limit=10)

    assert result == [unpublished_outbox]


@pytest.mark.asyncio
async def test_list_unpublished_respects_limit(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)

    first_outbox = create_outbox()
    second_outbox = create_outbox()

    await repo.add(first_outbox)
    await repo.add(second_outbox)
    await db_session.commit()

    result = await repo.list_unpublished(limit=1)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_mark_as_published_sets_published_at(db_session: AsyncSession) -> None:
    repo = OutboxRepository(db_session)
    outbox = create_outbox()

    await repo.add(outbox)
    await db_session.commit()

    await repo.mark_as_published(outbox.id)
    await db_session.commit()

    saved_outbox = await repo.get_by_id(outbox.id)

    assert saved_outbox is not None
    assert saved_outbox.published_at is not None
