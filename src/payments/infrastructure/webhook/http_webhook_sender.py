import asyncio
from typing import Any

import httpx

from core.config import Settings
from core.logging import get_logger
from payments.application.interfaces.webhook_sender import IWebhookSender
from payments.domain.entities.payment_entity import PaymentEntity

logger = get_logger(__name__)


class HttpWebhookSender(IWebhookSender):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send_payment_processed(self, payment: PaymentEntity) -> None:
        payload = self._build_payload(payment)

        for attempt in range(1, self.settings.WEBHOOK_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.WEBHOOK_TIMEOUT_SECONDS) as client:
                    response = await client.post(payment.webhook_url, json=payload)
                    response.raise_for_status()

                logger.info(
                    "Webhook sent: payment_id=%s webhook_url=%s attempt=%s",
                    payment.id,
                    payment.webhook_url,
                    attempt,
                )
                return

            except httpx.HTTPError as error:
                if attempt == self.settings.WEBHOOK_ATTEMPTS:
                    logger.exception(
                        "Webhook sending failed after retries: payment_id=%s webhook_url=%s attempts=%s",
                        payment.id,
                        payment.webhook_url,
                        self.settings.WEBHOOK_ATTEMPTS,
                    )
                    return

                delay_seconds = self.settings.WEBHOOK_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                logger.warning(
                    "Webhook sending failed, retrying: payment_id=%s webhook_url=%s attempt=%s delay_sec=%s error=%s",
                    payment.id,
                    payment.webhook_url,
                    attempt,
                    delay_seconds,
                    error,
                )
                await asyncio.sleep(delay_seconds)

    @staticmethod
    def _build_payload(payment: PaymentEntity) -> dict[str, Any]:
        return {
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "amount": str(payment.money.amount),
            "currency": payment.money.currency.value,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }
