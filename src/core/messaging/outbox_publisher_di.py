from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from payments.application.interfaces.event_publisher import IEventPublisher
from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.application.interfaces.unit_of_work import IUnitOfWork
from payments.application.outbox_publisher_service import OutboxPublisherService
from payments.infrastructure.messaging.event_publisher import EventPublisher


class OutboxPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    async def broker(self, settings: Settings) -> AsyncIterable[RabbitBroker]:
        broker = RabbitBroker(settings.rabbitmq_url)
        await broker.start()
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
