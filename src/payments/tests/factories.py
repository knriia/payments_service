from datetime import UTC, datetime
from decimal import Decimal

from uuid6 import uuid6

from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import Currency, Money, OutboxEventType, PaymentStatus


def create_payment(idempotency_key: str = "idempotency-key") -> PaymentEntity:
    return PaymentEntity(
        id=uuid6(),
        money=Money(amount=Decimal("100.00"), currency=Currency.RUB),
        description="test payment",
        metadata={"order_id": "order-1"},
        status=PaymentStatus.PENDING,
        idempotency_key=idempotency_key,
        webhook_url="https://example.com/webhook",
        created_at=datetime.now(UTC),
    )


def create_outbox() -> OutboxEntity:
    return OutboxEntity(
        id=uuid6(),
        event_type=OutboxEventType.PAYMENT_CREATED,
        payload={"payment_id": str(uuid6())},
        created_at=datetime.now(UTC),
    )
