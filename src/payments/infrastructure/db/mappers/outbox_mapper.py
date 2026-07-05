from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.value_objects import OutboxEventType
from payments.infrastructure.db.models.outbox_model import OutboxModel


def outbox_entity_to_outbox_model(outbox_entity: OutboxEntity) -> OutboxModel:
    return OutboxModel(
        id=outbox_entity.id,
        event_type=outbox_entity.event_type.value,
        payload=outbox_entity.payload,
        published_at=outbox_entity.published_at,
        created_at=outbox_entity.created_at,
    )


def outbox_model_to_outbox_entity(outbox_model: OutboxModel) -> OutboxEntity:
    return OutboxEntity(
        id=outbox_model.id,
        event_type=OutboxEventType(outbox_model.event_type),
        payload=outbox_model.payload,
        published_at=outbox_model.published_at,
        created_at=outbox_model.created_at,
    )
