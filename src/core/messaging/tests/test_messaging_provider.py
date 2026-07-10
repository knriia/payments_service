import pytest
from dishka import Provider, Scope, make_async_container, provide
from faststream.rabbit import RabbitBroker

from core.config import Settings
from core.messaging.consumer_di import ConsumerProvider


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
            PUBLISH_LIMIT=100,
            POLL_INTERVAL_SECONDS=2,
            RETRY_HEADER="x-retry-count",
            LAST_ERROR_HEADER="x-last-error",
            MAX_RETRY_COUNT=3,
            BASE_RETRY_DELAY_SECONDS=2,
            WEBHOOK_ATTEMPTS=3,
            WEBHOOK_BASE_DELAY_SECONDS=2,
            WEBHOOK_TIMEOUT_SECONDS=5,
            PAYMENT_GATEWAY_SUCCESS_RATE=0.9,
            PAYMENT_GATEWAY_MIN_DELAY_SECONDS=2,
            PAYMENT_GATEWAY_MAX_DELAY_SECONDS=5,
        )


@pytest.mark.asyncio
async def test_container_resolves_rabbit_broker() -> None:
    container = make_async_container(SettingsTestProvider(), ConsumerProvider())
    broker = await container.get(RabbitBroker)

    assert isinstance(broker, RabbitBroker)

    await container.close()
