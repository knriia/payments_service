# ruff: noqa: S311

import asyncio
import random

from core.config import Settings
from payments.application.interfaces.payment_gateway import IPaymentGateway
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import PaymentGatewayResult


class FakePaymentGateway(IPaymentGateway):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def process(self, payment_entity: PaymentEntity) -> PaymentGatewayResult:
        await asyncio.sleep(
            random.uniform(
                self.settings.PAYMENT_GATEWAY_MIN_DELAY_SECONDS,
                self.settings.PAYMENT_GATEWAY_MAX_DELAY_SECONDS,
            )
        )

        if random.random() < self.settings.PAYMENT_GATEWAY_SUCCESS_RATE:
            return PaymentGatewayResult.SUCCEEDED

        return PaymentGatewayResult.FAILED
