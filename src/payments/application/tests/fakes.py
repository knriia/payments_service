from uuid import UUID

from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.interfaces.outbox_repository import IOutboxRepository
from payments.domain.interfaces.payment_repository import IPaymentRepository
from payments.domain.interfaces.unit_of_work import IUnitOfWork


class FakePaymentRepository(IPaymentRepository):
    def __init__(self) -> None:
        self.payments: list[PaymentEntity] = []

    async def add(self, payment_entity: PaymentEntity) -> None:
        self.payments.append(payment_entity)

    async def get_by_id(self, payment_id: UUID) -> PaymentEntity | None:
        return next((p for p in self.payments if p.id == payment_id), None)

    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentEntity | None:
        return next((p for p in self.payments if p.idempotency_key == idempotency_key), None)


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeOutboxRepository(IOutboxRepository):
    def __init__(self) -> None:
        self.outbox_records: list[OutboxEntity] = []

    async def add(self, outbox_entity: OutboxEntity) -> None:
        self.outbox_records.append(outbox_entity)

    async def get_by_id(self, outbox_id: UUID) -> OutboxEntity | None:
        return next((o for o in self.outbox_records if o.id == outbox_id), None)
