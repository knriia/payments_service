import pytest
from uuid6 import uuid6

from payments.application.payment_service import PaymentService
from payments.application.tests.fakes import (
    FakeOutboxRepository,
    FakePaymentGateway,
    FakePaymentRepository,
    FakeUnitOfWork,
    FakeWebhookSender,
)
from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import PaymentGatewayResult, PaymentStatus
from payments.tests.factories import create_payment


def create_payment_service(
    uow: FakeUnitOfWork,
    payment_repo: FakePaymentRepository,
    outbox_repo: FakeOutboxRepository,
    payment_gateway: FakePaymentGateway,
    webhook_sender: FakeWebhookSender | None = None,
) -> PaymentService:
    return PaymentService(
        uow=uow,
        payment_repo=payment_repo,
        outbox_repo=outbox_repo,
        payment_gateway=payment_gateway,
        webhook_sender=webhook_sender or FakeWebhookSender(),
    )


@pytest.mark.asyncio
async def test_create_payment_saves_payment_and_outbox_and_commits() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    payment = create_payment()
    payment_created = await payment_service.create_payment(payment_entity=payment)
    assert payment_created == payment
    assert payment_repo.payments == [payment]
    assert len(outbox_repo.outbox_records) == 1
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_create_payment_creates_outbox_with_payment_payload() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    payment = create_payment()

    await payment_service.create_payment(payment_entity=payment)

    outbox = outbox_repo.outbox_records[0]

    assert outbox.payload == {
        "payment_id": str(payment.id),
        "amount": str(payment.money.amount),
        "currency": payment.money.currency.value,
        "webhook_url": payment.webhook_url,
    }


@pytest.mark.asyncio
async def test_create_payment_returns_existing_payment_when_idempotency_key_exists() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    existing_payment = create_payment(idempotency_key="same-key")
    new_payment = create_payment(idempotency_key="same-key")
    payment_repo.payments.append(existing_payment)

    result = await payment_service.create_payment(payment_entity=new_payment)

    assert result == existing_payment
    assert payment_repo.payments == [existing_payment]
    assert outbox_repo.outbox_records == []
    assert uow.committed is False
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_create_payment_rolls_back_when_payment_repository_fails() -> None:
    class FailingPaymentRepository(FakePaymentRepository):
        async def add(self, payment_entity: PaymentEntity) -> None:
            raise RuntimeError

    uow = FakeUnitOfWork()
    payment_repo = FailingPaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    payment = create_payment()

    with pytest.raises(RuntimeError):
        await payment_service.create_payment(payment_entity=payment)

    assert payment_repo.payments == []
    assert outbox_repo.outbox_records == []
    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_create_payment_rolls_back_when_outbox_repository_fails() -> None:
    class FailingOutboxRepository(FakeOutboxRepository):
        async def add(self, outbox_entity: OutboxEntity) -> None:
            raise RuntimeError

    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FailingOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    payment = create_payment()

    with pytest.raises(RuntimeError):
        await payment_service.create_payment(payment_entity=payment)

    assert payment_repo.payments == [payment]
    assert outbox_repo.outbox_records == []
    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_get_payment_by_id_returns_payment_when_payment_exists() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)
    payment = create_payment()
    payment_repo.payments.append(payment)

    result = await payment_service.get_payment_by_id(payment_id=payment.id)

    assert result == payment


@pytest.mark.asyncio
async def test_get_payment_by_id_returns_none_when_payment_not_found() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway)

    result = await payment_service.get_payment_by_id(payment_id=uuid6())
    assert result is None


@pytest.mark.asyncio
async def test_process_payment_marks_payment_as_succeeded_and_commits() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    webhook_sender = FakeWebhookSender()
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway, webhook_sender)
    payment = create_payment()
    payment_repo.payments.append(payment)

    result = await payment_service.process_payment(payment_id=payment.id)

    assert result == payment
    assert payment.status == PaymentStatus.SUCCEEDED
    assert payment.processed_at is not None
    assert payment_gateway.processed_payments == [payment]
    assert payment_repo.updated_payments == [payment]
    assert webhook_sender.sent_payments == [payment]
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_process_payment_marks_payment_as_failed_and_commits() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.FAILED)
    webhook_sender = FakeWebhookSender()
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway, webhook_sender)
    payment = create_payment()
    payment_repo.payments.append(payment)

    result = await payment_service.process_payment(payment_id=payment.id)

    assert result == payment
    assert payment.status == PaymentStatus.FAILED
    assert payment.processed_at is not None
    assert payment_gateway.processed_payments == [payment]
    assert payment_repo.updated_payments == [payment]
    assert webhook_sender.sent_payments == [payment]
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_process_payment_returns_none_when_payment_not_found() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    webhook_sender = FakeWebhookSender()
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway, webhook_sender)

    result = await payment_service.process_payment(payment_id=uuid6())

    assert result is None
    assert payment_repo.updated_payments == []
    assert payment_gateway.processed_payments == []
    assert webhook_sender.sent_payments == []
    assert uow.committed is False
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_process_payment_skips_gateway_and_webhook_when_payment_already_processed() -> None:
    uow = FakeUnitOfWork()
    payment_repo = FakePaymentRepository()
    outbox_repo = FakeOutboxRepository()
    payment_gateway = FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)
    webhook_sender = FakeWebhookSender()
    payment_service = create_payment_service(uow, payment_repo, outbox_repo, payment_gateway, webhook_sender)
    payment = create_payment()
    payment.mark_succeeded(payment.created_at)
    payment_repo.payments.append(payment)

    result = await payment_service.process_payment(payment_id=payment.id)

    assert result == payment
    assert payment_gateway.processed_payments == []
    assert payment_repo.updated_payments == []
    assert webhook_sender.sent_payments == []
    assert uow.committed is False
    assert uow.rolled_back is False
