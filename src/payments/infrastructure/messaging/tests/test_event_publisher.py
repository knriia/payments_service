from typing import Any

import pytest
from faststream.rabbit import RabbitExchange

from core.messaging.event_names import PAYMENTS_NEW_QUEUE
from core.messaging.events import payments_exchange
from payments.application.message.message_mappers import payment_created_message_from_outbox
from payments.domain.value_objects import OutboxEventType
from payments.infrastructure.messaging.event_publisher import EventPublisher
from payments.tests.factories import create_payment_created_outbox


class FakeRabbitBroker:
    def __init__(self) -> None:
        self.published_messages: list[dict[str, Any]] = []

    async def publish(
        self,
        message: dict[str, Any],
        exchange: RabbitExchange,
        routing_key: str,
    ) -> None:
        self.published_messages.append(
            {
                "message": message,
                "exchange": exchange,
                "routing_key": routing_key,
            }
        )


@pytest.mark.asyncio
async def test_event_publisher_publishes_payment_created_message() -> None:
    broker = FakeRabbitBroker()
    publisher = EventPublisher(broker=broker)  # type: ignore[arg-type]
    outbox = create_payment_created_outbox()
    message = payment_created_message_from_outbox(outbox)

    await publisher.publish(event_type=OutboxEventType.PAYMENT_CREATED, payload=message)

    assert broker.published_messages == [
        {
            "message": {
                "payment_id": str(message.payment_id),
                "amount": str(message.amount),
                "currency": message.currency.value,
                "webhook_url": str(message.webhook_url),
            },
            "exchange": payments_exchange,
            "routing_key": PAYMENTS_NEW_QUEUE,
        }
    ]
