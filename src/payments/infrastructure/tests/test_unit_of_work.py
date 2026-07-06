import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from payments.infrastructure.db.repositories.outbox_repository import OutboxRepository
from payments.infrastructure.db.repositories.payment_repository import PaymentRepository
from payments.infrastructure.db.unit_of_work import UnitOfWork
from payments.infrastructure.tests.factories import create_outbox, create_payment


@pytest.mark.asyncio
async def test_commit_saves_payment_and_outbox(db_session: AsyncSession) -> None:
    uow = UnitOfWork(session=db_session)
    payment_repo = PaymentRepository(session=db_session)
    outbox_repo = OutboxRepository(session=db_session)

    payment = create_payment()
    outbox = create_outbox()

    async with uow:
        await payment_repo.add(payment)
        await outbox_repo.add(outbox)
        await uow.commit()

    saved_payment = await payment_repo.get_by_id(payment.id)
    saved_outbox = await outbox_repo.get_by_id(outbox.id)

    assert saved_payment == payment
    assert saved_outbox == outbox


@pytest.mark.asyncio
async def test_rollback_does_not_save_payment_and_outbox(db_session: AsyncSession) -> None:
    uow = UnitOfWork(session=db_session)
    payment_repo = PaymentRepository(session=db_session)
    outbox_repo = OutboxRepository(session=db_session)

    payment = create_payment()
    outbox = create_outbox()

    async with uow:
        await payment_repo.add(payment)
        await outbox_repo.add(outbox)
        await uow.rollback()

    assert await payment_repo.get_by_id(payment.id) is None
    assert await outbox_repo.get_by_id(outbox.id) is None


@pytest.mark.asyncio
async def test_context_manager_rolls_back_when_exception_raised(db_session: AsyncSession) -> None:
    uow = UnitOfWork(session=db_session)
    payment_repo = PaymentRepository(session=db_session)
    outbox_repo = OutboxRepository(session=db_session)

    payment = create_payment()
    outbox = create_outbox()

    with pytest.raises(RuntimeError):
        async with uow:
            await payment_repo.add(payment)
            await outbox_repo.add(outbox)
            raise RuntimeError

    assert await payment_repo.get_by_id(payment.id) is None
    assert await outbox_repo.get_by_id(outbox.id) is None
