from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from payments.domain.value_objects import Currency, PaymentStatus


class InputPaymentDTO(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    webhook_url: str


class OutputPaymentDTO(InputPaymentDTO):
    id: UUID
    status: PaymentStatus
    created_at: datetime
    processed_at: datetime | None
