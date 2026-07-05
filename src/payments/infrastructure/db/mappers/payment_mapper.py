from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import Currency, Money, PaymentStatus
from payments.infrastructure.db.models.payment_model import PaymentModel


def payment_entity_to_payment_model(payment_entity: PaymentEntity) -> PaymentModel:
    return PaymentModel(
        id=payment_entity.id,
        amount=payment_entity.money.amount,
        currency=payment_entity.money.currency.value,
        description=payment_entity.description,
        payment_metadata=payment_entity.metadata,
        status=payment_entity.status.value,
        idempotency_key=payment_entity.idempotency_key,
        webhook_url=payment_entity.webhook_url,
        created_at=payment_entity.created_at,
        processed_at=payment_entity.processed_at,
    )


def payment_model_to_payment_entity(payment_model: PaymentModel) -> PaymentEntity:
    return PaymentEntity(
        id=payment_model.id,
        money=Money(amount=payment_model.amount, currency=Currency(payment_model.currency)),
        description=payment_model.description,
        metadata=payment_model.payment_metadata,
        status=PaymentStatus(payment_model.status),
        idempotency_key=payment_model.idempotency_key,
        webhook_url=payment_model.webhook_url,
        created_at=payment_model.created_at,
        processed_at=payment_model.processed_at,
    )
