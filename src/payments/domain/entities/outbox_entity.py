from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from uuid6 import uuid6

from payments.domain.exceptions import OutboxAlreadyPublished
from payments.domain.value_objects import OutboxEventType


@dataclass(kw_only=True)
class OutboxEntity:
    id: UUID
    event_type: OutboxEventType
    payload: dict[str, Any]
    created_at: datetime
    published_at: datetime | None = None

    @classmethod
    def create(
        cls,
        payload: dict[str, Any],
    ) -> "OutboxEntity":
        return OutboxEntity(
            id=uuid6(),
            event_type=OutboxEventType.PAYMENT_CREATED,
            payload=payload,
            created_at=datetime.now(UTC),
        )

    def mark_published(self, published_at: datetime) -> None:
        if self.published_at is not None:
            raise OutboxAlreadyPublished(f"OutboxRecord {self.id} already published")
        self.published_at = published_at
