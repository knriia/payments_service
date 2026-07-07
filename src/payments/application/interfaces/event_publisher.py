from abc import ABC, abstractmethod

from payments.application.message.message_dto import PaymentCreatedMessageDTO
from payments.domain.value_objects import OutboxEventType


class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event_type: OutboxEventType, payload: PaymentCreatedMessageDTO) -> None:
        pass
