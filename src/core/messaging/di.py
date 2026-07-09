from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from core.messaging.broker import create_broker
from core.messaging.events import payments_dlq, payments_exchange, payments_new_queue, payments_retry_queue
from payments.application.interfaces.event_publisher import IEventPublisher
from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.application.interfaces.unit_of_work import IUnitOfWork
from payments.application.outbox_publisher_service import OutboxPublisherService
from payments.infrastructure.messaging.event_publisher import EventPublisher


class OutboxPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    async def broker(self, settings: Settings) -> AsyncIterable[RabbitBroker]:
        broker = create_broker(settings=settings)
        await broker.start()
        exchange = await broker.declare_exchange(payments_exchange)
        payments_queue = await broker.declare_queue(payments_new_queue)
        retry_queue = await broker.declare_queue(payments_retry_queue)
        dlq_queue = await broker.declare_queue(payments_dlq)
        await payments_queue.bind(exchange, routing_key=payments_new_queue.routing())
        await retry_queue.bind(exchange, routing_key=payments_retry_queue.routing())
        await dlq_queue.bind(exchange, routing_key=payments_dlq.routing())

        try:
            yield broker
        finally:
            await broker.stop()

    @provide(scope=Scope.REQUEST)
    def event_publisher(self, broker: RabbitBroker) -> IEventPublisher:
        return EventPublisher(broker=broker)

    @provide(scope=Scope.REQUEST)
    def outbox_publisher_service(
        self,
        unit_of_work: IUnitOfWork,
        outbox_repository: IOutboxRepository,
        event_publisher: IEventPublisher,
    ) -> OutboxPublisherService:
        return OutboxPublisherService(uow=unit_of_work, outbox_repo=outbox_repository, event_publisher=event_publisher)
