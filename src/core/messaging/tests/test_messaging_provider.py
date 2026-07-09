import pytest
from dishka import Provider, Scope, make_async_container, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from core.messaging.outbox_publisher_di import OutboxPublisherProvider


class SettingsTestProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings(
            DB_HOST="localhost",
            DB_PORT="5432",
            DB_NAME="test",
            DB_USER="test",
            DB_PASSWORD="test",  # noqa: S106
            RABBIT_HOST="localhost",
            RABBIT_PORT="5672",
            RABBIT_USER="guest",
            RABBIT_PASS="guest",  # noqa: S106
            API_KEY="test-api-key",
        )


@pytest.mark.asyncio
async def test_container_resolves_rabbit_broker() -> None:
    container = make_async_container(SettingsTestProvider(), OutboxPublisherProvider())
    broker = await container.get(RabbitBroker)

    assert isinstance(broker, RabbitBroker)

    await container.close()
