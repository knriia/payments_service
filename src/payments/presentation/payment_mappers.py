from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import Money
from payments.presentation.payment_dto import InputPaymentDTO, OutputPaymentDTO


def payment_entity_to_dto(payment_entity: PaymentEntity) -> OutputPaymentDTO:
    return OutputPaymentDTO(
        id=payment_entity.id,
        amount=payment_entity.money.amount,
        currency=payment_entity.money.currency,
        description=payment_entity.description,
        metadata=payment_entity.metadata,
        status=payment_entity.status,
        webhook_url=payment_entity.webhook_url,
        created_at=payment_entity.created_at,
        processed_at=payment_entity.processed_at,
    )


def payment_dto_to_entity(payment_dto: InputPaymentDTO, idempotency_key: str) -> PaymentEntity:
    return PaymentEntity.create(
        money=Money(amount=payment_dto.amount, currency=payment_dto.currency),
        description=payment_dto.description,
        metadata=payment_dto.metadata,
        idempotency_key=idempotency_key,
        webhook_url=payment_dto.webhook_url,
    )
