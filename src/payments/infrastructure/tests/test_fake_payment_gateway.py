import pytest

from core.config import Settings
from payments.domain.value_objects import PaymentGatewayResult
from payments.infrastructure.gateway.fake_payment_gateway import FakePaymentGateway
from payments.tests.factories import create_payment


def create_settings(
    success_rate: float,
    min_delay_seconds: float = 0,
    max_delay_seconds: float = 0,
) -> Settings:
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
        PAYMENT_GATEWAY_SUCCESS_RATE=success_rate,
        PAYMENT_GATEWAY_MIN_DELAY_SECONDS=min_delay_seconds,
        PAYMENT_GATEWAY_MAX_DELAY_SECONDS=max_delay_seconds,
    )


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_succeeded_when_success_rate_is_1() -> None:
    gateway = FakePaymentGateway(settings=create_settings(success_rate=1))
    payment = create_payment()

    result = await gateway.process(payment)

    assert result == PaymentGatewayResult.SUCCEEDED


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_failed_when_success_rate_is_0() -> None:
    gateway = FakePaymentGateway(settings=create_settings(success_rate=0))
    payment = create_payment()

    result = await gateway.process(payment)

    assert result == PaymentGatewayResult.FAILED


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_about_10_percent_failures() -> None:
    gateway = FakePaymentGateway(settings=create_settings(success_rate=0.9))
    payment = create_payment()

    runs = 1000
    results = [await gateway.process(payment) for _ in range(runs)]

    failed_count = results.count(PaymentGatewayResult.FAILED)
    failed_rate = failed_count / runs

    assert 0.05 <= failed_rate <= 0.15
