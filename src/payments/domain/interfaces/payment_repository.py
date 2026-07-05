from abc import ABC, abstractmethod
from uuid import UUID

from payments.domain.entities.payment_entity import PaymentEntity


class IPaymentRepository(ABC):
    @abstractmethod
    async def add(self, payment: PaymentEntity) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> PaymentEntity | None:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentEntity | None:
        pass
