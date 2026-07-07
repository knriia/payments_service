from payments.domain.entities.payment_entity import PaymentEntity
from payments.presentation.payment_dto import InputPaymentDTO, OutputPaymentDTO


def payment_entity_to_dto(payment_entity: PaymentEntity) -> OutputPaymentDTO:
    return OutputPaymentDTO(
        id=payment_entity.id,
        money=payment_entity.money,
        description=payment_entity.description,
        metadata=payment_entity.metadata,
        status=payment_entity.status,
        idempotency_key=payment_entity.idempotency_key,
        webhook_url=payment_entity.webhook_url,
        created_at=payment_entity.created_at,
        processed_at=payment_entity.processed_at,
    )


def payment_dto_to_entity(payment_dto: InputPaymentDTO, idempotency_key: str) -> PaymentEntity:
    return PaymentEntity.create(
        money=payment_dto.money,
        description=payment_dto.description,
        metadata=payment_dto.metadata,
        idempotency_key=idempotency_key,
        webhook_url=payment_dto.webhook_url,
    )
