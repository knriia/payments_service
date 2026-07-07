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
    monkeypatch.setenv("RABBIT_USER", "guest")
    monkeypatch.setenv("RABBIT_PASS", "guest")
    monkeypatch.setenv("API_KEY", "test-api-key")

    container = create_container()

    async with container() as request_container:
        payment_service = await request_container.get(PaymentService)

    assert isinstance(payment_service, PaymentService)

    await container.close()
