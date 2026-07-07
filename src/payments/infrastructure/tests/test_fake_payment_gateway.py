import pytest

from payments.domain.value_objects import PaymentGatewayResult
from payments.infrastructure.gateway.fake_payment_gateway import FakePaymentGateway
from payments.tests.factories import create_payment


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_succeeded_when_success_rate_is_1() -> None:
    gateway = FakePaymentGateway(success_rate=1, min_delay_seconds=0, max_delay_seconds=0)
    payment = create_payment()

    result = await gateway.process(payment)

    assert result == PaymentGatewayResult.SUCCEEDED


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_failed_when_success_rate_is_0() -> None:
    gateway = FakePaymentGateway(success_rate=0, min_delay_seconds=0, max_delay_seconds=0)
    payment = create_payment()

    result = await gateway.process(payment)

    assert result == PaymentGatewayResult.FAILED


@pytest.mark.asyncio
async def test_fake_payment_gateway_returns_about_10_percent_failures() -> None:
    gateway = FakePaymentGateway(success_rate=0.9, min_delay_seconds=0, max_delay_seconds=0)
    payment = create_payment()

    runs = 1000
    results = [await gateway.process(payment) for _ in range(runs)]

    failed_count = results.count(PaymentGatewayResult.FAILED)
    failed_rate = failed_count / runs

    assert 0.05 <= failed_rate <= 0.15
