from datetime import UTC, datetime
from uuid import UUID

from core.logging import get_logger
from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.application.interfaces.payment_gateway import IPaymentGateway
from payments.application.interfaces.payment_repository import IPaymentRepository
from payments.application.interfaces.unit_of_work import IUnitOfWork
from payments.application.interfaces.webhook_sender import IWebhookSender
from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.exceptions import DuplicateIdempotencyKey
from payments.domain.value_objects import PaymentGatewayResult, PaymentStatus

logger = get_logger(__name__)


class PaymentService:
    def __init__(
        self,
        uow: IUnitOfWork,
        payment_repo: IPaymentRepository,
        outbox_repo: IOutboxRepository,
        payment_gateway: IPaymentGateway,
        webhook_sender: IWebhookSender,
    ):
        self.uow = uow
        self.payment_repo = payment_repo
        self.outbox_repo = outbox_repo
        self.payment_gateway = payment_gateway
        self.webhook_sender = webhook_sender

    async def create_payment(self, payment_entity: PaymentEntity) -> PaymentEntity:
        existing_payload = await self.get_payment_idempotency_key(payment_entity.idempotency_key)
        if existing_payload:
            logger.info(
                "Payment idempotency hit: payment_id=%s idempotency_key=%s",
                existing_payload.id,
                existing_payload.idempotency_key,
            )
            return existing_payload

        try:
            async with self.uow:
                await self.payment_repo.add(payment_entity=payment_entity)
                await self._create_outbox(payment_entity=payment_entity)
                await self.uow.commit()
                logger.info("Payment created: payment_id=%s outbox_created=true", payment_entity.id)

        except DuplicateIdempotencyKey:
            existing_payment = await self.get_payment_idempotency_key(payment_entity.idempotency_key)
            if existing_payment is not None:
                logger.info(
                    "Payment idempotency race resolved: payment_id=%s idempotency_key=%s",
                    existing_payment.id,
                    existing_payment.idempotency_key,
                )
                return existing_payment
            raise

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

    async def process_payment(self, payment_id: UUID) -> PaymentEntity | None:
        payment = await self.get_payment_by_id(payment_id=payment_id)
        if payment is None:
            logger.warning("Payment processing skipped: payment_id=%s reason=not_found", payment_id)
            return None

        if payment.status != PaymentStatus.PENDING:
            logger.info("Payment processing skipped: payment_id=%s status=%s", payment.id, payment.status)
            return payment

        result = await self.payment_gateway.process(payment_entity=payment)

        async with self.uow:
            if result == PaymentGatewayResult.SUCCEEDED:
                payment.mark_succeeded(datetime.now(UTC))
            else:
                payment.mark_failed(datetime.now(UTC))

            await self.payment_repo.update(payment_entity=payment)
            await self.uow.commit()
            logger.info("Payment processed: payment_id=%s status=%s", payment.id, payment.status)

        await self.webhook_sender.send_payment_processed(payment)
        return payment
