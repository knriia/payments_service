from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.interfaces.outbox_repository import IOutboxRepository
from payments.infrastructure.db.mappers.outbox_mapper import (
    outbox_entity_to_outbox_model,
    outbox_model_to_outbox_entity,
)
from payments.infrastructure.db.models import OutboxModel


class OutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, outbox_entity: OutboxEntity) -> None:
        outbox_model = outbox_entity_to_outbox_model(outbox_entity)
        self.session.add(outbox_model)

    async def get_by_id(self, outbox_id: UUID) -> OutboxEntity | None:
        model = await self.session.get(OutboxModel, outbox_id)
        if model is None:
            return None

        return outbox_model_to_outbox_entity(outbox_model=model)
