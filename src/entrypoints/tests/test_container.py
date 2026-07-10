import pytest

from entrypoints.container import create_container
from payments.application.payment_service import PaymentService


@pytest.mark.asyncio
async def test_container_resolves_payment_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test")
    monkeypatch.setenv("DB_USER", "test")
    monkeypatch.setenv("DB_PASSWORD", "test")
    monkeypatch.setenv("RABBIT_HOST", "localhost")
    monkeypatch.setenv("RABBIT_PORT", "5672")
    monkeypatch.setenv("RABBIT_USER", "guest")
    monkeypatch.setenv("RABBIT_PASS", "guest")
    monkeypatch.setenv("API_KEY", "test-api-key")
    monkeypatch.setenv("PUBLISH_LIMIT", "100")
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "2")
    monkeypatch.setenv("RETRY_HEADER", "x-retry-count")
    monkeypatch.setenv("LAST_ERROR_HEADER", "x-last-error")
    monkeypatch.setenv("MAX_RETRY_COUNT", "3")
    monkeypatch.setenv("BASE_RETRY_DELAY_SECONDS", "2")
    monkeypatch.setenv("WEBHOOK_ATTEMPTS", "3")
    monkeypatch.setenv("WEBHOOK_BASE_DELAY_SECONDS", "2")
    monkeypatch.setenv("WEBHOOK_TIMEOUT_SECONDS", "5")
    monkeypatch.setenv("PAYMENT_GATEWAY_SUCCESS_RATE", "0.9")
    monkeypatch.setenv("PAYMENT_GATEWAY_MIN_DELAY_SECONDS", "2")
    monkeypatch.setenv("PAYMENT_GATEWAY_MAX_DELAY_SECONDS", "5")

    container = create_container()

    async with container() as request_container:
        payment_service = await request_container.get(PaymentService)

    assert isinstance(payment_service, PaymentService)

    await container.close()
