# ruff: noqa: S311

import asyncio
import random

from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.interfaces.payment_gateway import IPaymentGateway
from payments.domain.value_objects import PaymentGatewayResult


class FakePaymentGateway(IPaymentGateway):
    def __init__(
        self,
        success_rate: float = 0.9,
        min_delay_seconds: float = 2,
        max_delay_seconds: float = 5,
    ) -> None:
        self.success_rate = success_rate
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds

    async def process(self, payment_entity: PaymentEntity) -> PaymentGatewayResult:
        await asyncio.sleep(random.uniform(self.min_delay_seconds, self.max_delay_seconds))

        if random.random() < self.success_rate:
            return PaymentGatewayResult.SUCCEEDED

        return PaymentGatewayResult.FAILED
