from abc import ABC, abstractmethod
from uuid import UUID

from payments.domain.entities.outbox_entity import OutboxEntity


class IOutboxRepository(ABC):
    @abstractmethod
    async def add(self, outbox: OutboxEntity) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, outbox_id: UUID) -> OutboxEntity | None:
        pass
