from datetime import UTC, datetime
from uuid import UUID

from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.interfaces.outbox_repository import IOutboxRepository
from payments.domain.interfaces.payment_gateway import IPaymentGateway
from payments.domain.interfaces.payment_repository import IPaymentRepository
from payments.domain.interfaces.unit_of_work import IUnitOfWork
from payments.domain.value_objects import PaymentGatewayResult


class PaymentService:
    def __init__(
        self,
        uow: IUnitOfWork,
        payment_repo: IPaymentRepository,
        outbox_repo: IOutboxRepository,
        payment_gateway: IPaymentGateway,
    ):
        self.uow = uow
        self.payment_repo = payment_repo
        self.outbox_repo = outbox_repo
        self.payment_gateway = payment_gateway

    async def create_payment(self, payment_entity: PaymentEntity) -> PaymentEntity:
        existing_payload = await self.get_payment_idempotency_key(payment_entity.idempotency_key)
        if existing_payload:
            return existing_payload

        async with self.uow:
            await self.payment_repo.add(payment_entity=payment_entity)
            await self._create_outbox(payment_entity=payment_entity)
            await self.uow.commit()

        return payment_entity

    async def get_payment_idempotency_key(self, idempotency_key: str) -> PaymentEntity | None:
        return await self.payment_repo.get_by_idempotency_key(idempotency_key=idempotency_key)

    async def get_payment_by_id(self, payment_id: UUID) -> PaymentEntity | None:
        return await self.payment_repo.get_by_id(payment_id=payment_id)

    async def _create_outbox(self, payment_entity: PaymentEntity) -> None:
        payload = {
            "payment_id": str(payment_entity.id),
            "amount": str(payment_entity.money.amount),
            "currency": payment_entity.money.currency.value,
            "webhook_url": payment_entity.webhook_url,
        }
        outbox_entity = OutboxEntity.create(payload=payload)
        await self.outbox_repo.add(outbox_entity=outbox_entity)

    async def get_outbox_payment_id(self, outbox_id: UUID) -> OutboxEntity | None:
        return await self.outbox_repo.get_by_id(outbox_id=outbox_id)

    async def process_payment(self, payment_id: UUID) -> PaymentEntity | None:
        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            return None

        result = await self.payment_gateway.process(payment_entity=payment)

        async with self.uow:
            if result == PaymentGatewayResult.SUCCEEDED:
                payment.mark_succeeded(datetime.now(UTC))
            else:
                payment.mark_failed(datetime.now(UTC))

            await self.payment_repo.update(payment_entity=payment)
            await self.uow.commit()

        return payment
