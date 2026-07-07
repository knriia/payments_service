from typing import Any

from payments.application.message.message_dto import PaymentCreatedMessageDTO
from payments.domain.entities.outbox_entity import OutboxEntity


def payment_created_message_from_outbox(outbox_entity: OutboxEntity) -> PaymentCreatedMessageDTO:
    return PaymentCreatedMessageDTO.model_validate(outbox_entity.payload)


def payment_created_message_to_payload(message: PaymentCreatedMessageDTO) -> dict[str, Any]:
    return message.model_dump(mode="json")
