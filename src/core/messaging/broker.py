from faststream.rabbit import RabbitBroker

from core.config import Settings


def create_broker(settings: Settings) -> RabbitBroker:
    return RabbitBroker(settings.rabbitmq_url)
