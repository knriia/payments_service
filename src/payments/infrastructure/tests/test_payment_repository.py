import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid6

from payments.domain.exceptions import DuplicateIdempotencyKey
from payments.infrastructure.db.repositories.payment_repository import PaymentRepository
from payments.tests.factories import create_payment


@pytest.mark.asyncio
async def test_add_and_get_by_id_returns_payment(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)
    payment = create_payment()
    await repo.add(payment)
    await db_session.commit()
    saved_payment = await repo.get_by_id(payment.id)
    assert saved_payment == payment


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_payment_not_found(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)
    payment = await repo.get_by_id(uuid6())
    assert payment is None


@pytest.mark.asyncio
async def test_get_by_idempotency_key_returns_payment(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)
    payment = create_payment(idempotency_key="same-key")

    await repo.add(payment)
    await db_session.commit()

    saved_payment = await repo.get_by_idempotency_key("same-key")

    assert saved_payment == payment


@pytest.mark.asyncio
async def test_get_by_idempotency_key_returns_none_when_payment_not_found(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = await repo.get_by_idempotency_key("missing-key")

    assert payment is None


@pytest.mark.asyncio
async def test_add_raises_duplicate_idempotency_key_when_key_already_exists(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)
    payment = create_payment(idempotency_key="same-key")
    duplicate_payment = create_payment(idempotency_key="same-key")

    await repo.add(payment)
    await db_session.commit()

    with pytest.raises(DuplicateIdempotencyKey):
        await repo.add(duplicate_payment)
