from decimal import Decimal
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict

from payments.domain.value_objects import Currency


class PaymentCreatedMessageDTO(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: Currency
    webhook_url: AnyUrl

    model_config = ConfigDict(frozen=True)
