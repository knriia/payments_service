from abc import ABC, abstractmethod

from payments.domain.entities.payment_entity import PaymentEntity


class IWebhookSender(ABC):
    @abstractmethod
    async def send_payment_processed(self, payment: PaymentEntity) -> None:
        pass
