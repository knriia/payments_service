from faststream.rabbit import RabbitExchange, RabbitQueue

from core.messaging.event_names import (
    PAYMENTS_DLQ,
    PAYMENTS_EXCHANGE,
    PAYMENTS_NEW_QUEUE,
    PAYMENTS_RETRY_QUEUE,
)

payments_exchange = RabbitExchange(name=PAYMENTS_EXCHANGE, durable=True)

payments_new_queue = RabbitQueue(name=PAYMENTS_NEW_QUEUE, durable=True, routing_key=PAYMENTS_NEW_QUEUE)

payments_retry_queue = RabbitQueue(
    name=PAYMENTS_RETRY_QUEUE,
    durable=True,
    routing_key=PAYMENTS_RETRY_QUEUE,
    arguments={
        "x-dead-letter-exchange": PAYMENTS_EXCHANGE,
        "x-dead-letter-routing-key": PAYMENTS_NEW_QUEUE,
    },
)

payments_dlq = RabbitQueue(
    name=PAYMENTS_DLQ,
    durable=True,
    routing_key=PAYMENTS_DLQ,
)
