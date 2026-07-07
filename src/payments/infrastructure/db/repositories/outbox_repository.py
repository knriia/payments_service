from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.domain.entities.outbox_entity import OutboxEntity
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

    async def list_unpublished(self, limit: int) -> list[OutboxEntity]:
        stmt = (
            select(OutboxModel).where(OutboxModel.published_at.is_(None)).order_by(OutboxModel.created_at).limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [outbox_model_to_outbox_entity(outbox_model=model) for model in models]

    async def mark_as_published(self, outbox_id: UUID) -> None:
        model = await self.session.get(OutboxModel, outbox_id)
        if model is None:
            return

        outbox = outbox_model_to_outbox_entity(outbox_model=model)
        published_at = datetime.now(UTC)
        outbox.mark_published(published_at)
        model.published_at = outbox.published_at
