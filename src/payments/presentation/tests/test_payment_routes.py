from collections.abc import AsyncIterable

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.config import Settings
from payments.application.payment_service import PaymentService
from payments.application.tests.fakes import (
    FakeOutboxRepository,
    FakePaymentGateway,
    FakePaymentRepository,
    FakeUnitOfWork,
)
from payments.domain.interfaces.payment_gateway import IPaymentGateway
from payments.domain.interfaces.unit_of_work import IUnitOfWork
from payments.domain.value_objects import PaymentGatewayResult
from payments.presentation.payment_routes import payment_router


class SettingsTestProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings(
            DB_HOST="localhost",
            DB_PORT="5432",
            DB_NAME="test",
            DB_USER="test",
            DB_PASSWORD="test",  # noqa: S106
            RABBIT_USER="guest",
            RABBIT_PASS="guest",  # noqa: S106
            API_KEY="test-api-key",
        )


class PaymentTestProvider(Provider):
    @provide(scope=Scope.APP)
    def payment_repo(self) -> FakePaymentRepository:
        return FakePaymentRepository()

    @provide(scope=Scope.APP)
    def outbox_repo(self) -> FakeOutboxRepository:
        return FakeOutboxRepository()

    @provide(scope=Scope.REQUEST)
    def uow(self) -> IUnitOfWork:
        return FakeUnitOfWork()

    @provide(scope=Scope.APP)
    def payment_gateway(self) -> IPaymentGateway:
        return FakePaymentGateway(result=PaymentGatewayResult.SUCCEEDED)

    @provide(scope=Scope.REQUEST)
    def payment_service(
        self,
        uow: IUnitOfWork,
        payment_repo: FakePaymentRepository,
        outbox_repo: FakeOutboxRepository,
        payment_gateway: IPaymentGateway,
    ) -> PaymentService:
        return PaymentService(
            uow=uow,
            payment_repo=payment_repo,
            outbox_repo=outbox_repo,
            payment_gateway=payment_gateway,
        )


@pytest_asyncio.fixture
async def client() -> AsyncIterable[AsyncClient]:
    app = FastAPI()
    app.include_router(payment_router)

    container = make_async_container(SettingsTestProvider(), PaymentTestProvider())
    setup_dishka(container, app)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

    await container.close()


PAYMENT_PAYLOAD = {
    "money": {
        "amount": "100.00",
        "currency": "RUB",
    },
    "description": "test payment",
    "metadata": {"order_id": "order-1"},
    "webhook_url": "https://example.com/webhook",
}


@pytest.mark.asyncio
async def test_create_payment_returns_202(client: AsyncClient) -> None:
    response = await client.post(
        "/payments",
        json=PAYMENT_PAYLOAD,
        headers={
            "X-API-Key": "test-api-key",
            "Idempotency-Key": "same-key",
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "pending"
    assert data["idempotency_key"] == "same-key"
    assert data["money"] == {"amount": "100.00", "currency": "RUB"}


@pytest.mark.asyncio
async def test_get_payment_returns_payment(client: AsyncClient) -> None:
    create_response = await client.post(
        "/payments",
        json=PAYMENT_PAYLOAD,
        headers={
            "X-API-Key": "test-api-key",
            "Idempotency-Key": "same-key",
        },
    )

    payment_id = create_response.json()["id"]
    response = await client.get(
        f"/payments/{payment_id}",
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


@pytest.mark.asyncio
async def test_get_missing_payment_returns_404(client: AsyncClient) -> None:
    response = await client.get(
        "/payments/01984536-e7b7-7110-b33f-3f1743f721aa",
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Payment not found"}


@pytest.mark.asyncio
async def test_create_payment_with_same_idempotency_key_returns_same_payment(client: AsyncClient) -> None:
    headers = {
        "X-API-Key": "test-api-key",
        "Idempotency-Key": "same-key",
    }

    first_response = await client.post("/payments", json=PAYMENT_PAYLOAD, headers=headers)
    second_response = await client.post("/payments", json=PAYMENT_PAYLOAD, headers=headers)

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert second_response.json()["id"] == first_response.json()["id"]


@pytest.mark.asyncio
async def test_create_payment_without_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/payments",
        json=PAYMENT_PAYLOAD,
        headers={"Idempotency-Key": "same-key"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_payment_with_invalid_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/payments",
        json=PAYMENT_PAYLOAD,
        headers={
            "X-API-Key": "wrong-key",
            "Idempotency-Key": "same-key",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_payment_without_idempotency_key_returns_422(client: AsyncClient) -> None:
    response = await client.post(
        "/payments",
        json=PAYMENT_PAYLOAD,
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 422
