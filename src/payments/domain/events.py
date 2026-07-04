from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from payments.domain.value_objects import PaymentStatus


@dataclass(frozen=True, slots=True)
class PaymentCreated:
    payment_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PaymentProcessed:
    payment_id: UUID
    status: PaymentStatus
    occurred_at: datetime
