from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from uuid6 import uuid6

from payments.domain.exceptions import InvalidStatusTransition
from payments.domain.value_objects import Money, PaymentStatus


@dataclass(kw_only=True)
class PaymentEntity:
    id: UUID
    money: Money
    description: str
    metadata: dict[str, Any]
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        money: Money,
        description: str,
        metadata: dict[str, Any],
        idempotency_key: str,
        webhook_url: str,
    ) -> "PaymentEntity":
        return PaymentEntity(
            id=uuid6(),
            money=money,
            description=description,
            metadata=metadata,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            webhook_url=webhook_url,
            created_at=datetime.now(UTC),
        )

    def mark_succeeded(self, processed_at: datetime) -> None:
        self._ensure_pending()
        self.status = PaymentStatus.SUCCEEDED
        self.processed_at = processed_at

    def mark_failed(self, processed_at: datetime) -> None:
        self._ensure_pending()
        self.status = PaymentStatus.FAILED
        self.processed_at = processed_at

    def _ensure_pending(self) -> None:
        if self.status != PaymentStatus.PENDING:
            raise InvalidStatusTransition(f"Cannot transition payment {self.id} from {self.status}")
