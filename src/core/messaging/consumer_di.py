from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from payments.infrastructure.messaging.consumer_handlers import PaymentConsumerRegistrar


class ConsumerProvider(Provider):
    @provide(scope=Scope.APP)
    def broker(self, settings: Settings) -> RabbitBroker:
        return RabbitBroker(settings.rabbitmq_url)

    @provide(scope=Scope.APP)
    def payment_consumer_registrar(
        self,
        broker: RabbitBroker,
        settings: Settings,
    ) -> PaymentConsumerRegistrar:
        return PaymentConsumerRegistrar(
            broker=broker,
            settings=settings,
        )
