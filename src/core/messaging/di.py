from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from core.messaging.broker import create_broker


class MessagingProvider(Provider):
    @provide(scope=Scope.APP)
    def broker(self, settings: Settings) -> RabbitBroker:
        return create_broker(settings=settings)
