from faststream.rabbit import RabbitBroker

from core.messaging.event_names import PAYMENTS_NEW_QUEUE
from core.messaging.events import payments_exchange
from payments.application.interfaces.event_publisher import IEventPublisher
from payments.application.message.message_dto import PaymentCreatedMessageDTO
from payments.application.message.message_mappers import payment_created_message_to_payload
from payments.domain.value_objects import OutboxEventType


class EventPublisher(IEventPublisher):
    def __init__(self, broker: RabbitBroker):
        self.broker = broker

    async def publish(self, event_type: OutboxEventType, payload: PaymentCreatedMessageDTO) -> None:
        if event_type == OutboxEventType.PAYMENT_CREATED:
            await self.broker.publish(
                message=payment_created_message_to_payload(payload),
                exchange=payments_exchange,
                routing_key=PAYMENTS_NEW_QUEUE,
            )

            return

        raise ValueError(f"Unsupported outbox event type: {event_type}")
