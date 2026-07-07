from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from payments.domain.value_objects import Money, PaymentStatus


class InputPaymentDTO(BaseModel):
    money: Money
    description: str
    metadata: dict[str, Any]
    webhook_url: str


class OutputPaymentDTO(InputPaymentDTO):
    id: UUID
    status: PaymentStatus
    idempotency_key: str
    created_at: datetime
    processed_at: datetime | None
