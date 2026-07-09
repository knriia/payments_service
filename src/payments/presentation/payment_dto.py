from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from payments.domain.value_objects import Currency, PaymentStatus


class InputPaymentDTO(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    webhook_url: HttpUrl


class OutputPaymentDTO(BaseModel):
    id: UUID
    status: PaymentStatus
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict[str, Any]
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
