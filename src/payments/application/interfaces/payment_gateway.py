from abc import ABC, abstractmethod

from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.value_objects import PaymentGatewayResult


class IPaymentGateway(ABC):
    @abstractmethod
    async def process(self, payment_entity: PaymentEntity) -> PaymentGatewayResult:
        pass
