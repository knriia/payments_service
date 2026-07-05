from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from payments.domain.exceptions import InvalidPaymentAmount


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class OutboxEventType(StrEnum):
    PAYMENT_CREATED = "payment.created"


@dataclass(kw_only=True, frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise InvalidPaymentAmount(f"Payment amount must be positive, got {self.amount}")
