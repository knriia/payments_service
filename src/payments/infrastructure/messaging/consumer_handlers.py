from dishka_faststream import FromDishka, inject
from faststream.rabbit import RabbitBroker, RabbitMessage

from core.config import Settings
from core.logging import get_logger
from core.messaging.event_names import PAYMENTS_DLQ, PAYMENTS_RETRY_QUEUE
from core.messaging.events import payments_exchange, payments_new_queue
from payments.application.message.message_dto import PaymentCreatedMessageDTO
from payments.application.message.message_mappers import payment_created_message_to_payload
from payments.application.payment_service import PaymentService

logger = get_logger(__name__)


class PaymentConsumerRegistrar:
    def __init__(self, broker: RabbitBroker, settings: Settings):
        self.broker = broker
        self.settings = settings

    def register(self) -> None:
        self.broker.subscriber(payments_new_queue)(inject(self.handle_payment_created))

    async def handle_payment_created(
        self,
        message: PaymentCreatedMessageDTO,
        raw_message: RabbitMessage,
        service: FromDishka[PaymentService],
    ) -> None:
        try:
            await service.process_payment(payment_id=message.payment_id)
        except Exception as error:
            await self.republish_failed_message(
                message=message,
                raw_message=raw_message,
                error=error,
            )

    async def republish_failed_message(
        self,
        message: PaymentCreatedMessageDTO,
        raw_message: RabbitMessage,
        error: Exception,
    ) -> None:
        retry_count = int(raw_message.headers.get(self.settings.RETRY_HEADER, 0))
        next_retry_count = retry_count + 1
        payload = payment_created_message_to_payload(message)

        if next_retry_count <= self.settings.MAX_RETRY_COUNT:
            delay_seconds = self.settings.BASE_RETRY_DELAY_SECONDS * (2 ** (next_retry_count - 1))
            logger.warning(
                "Payment message processing failed, republishing to retry: "
                "payment_id=%s retry_count=%s delay_seconds=%s error=%s",
                message.payment_id,
                next_retry_count,
                delay_seconds,
                error,
            )

            await self.broker.publish(
                message=payload,
                exchange=payments_exchange,
                routing_key=PAYMENTS_RETRY_QUEUE,
                headers={self.settings.RETRY_HEADER: next_retry_count},
                expiration=delay_seconds,
            )
            return

        logger.error(
            "Payment message processing failed, sending to DLQ: payment_id=%s retry_count=%s error=%s",
            message.payment_id,
            next_retry_count,
            error,
        )
        await self.broker.publish(
            message=payload,
            exchange=payments_exchange,
            routing_key=PAYMENTS_DLQ,
            headers={
                self.settings.RETRY_HEADER: next_retry_count,
                self.settings.LAST_ERROR_HEADER: str(error),
            },
        )
