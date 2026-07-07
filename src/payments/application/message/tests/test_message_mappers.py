import pytest
from pydantic import ValidationError

from payments.application.message.message_mappers import (
    payment_created_message_from_outbox,
    payment_created_message_to_payload,
)
from payments.domain.value_objects import Currency
from payments.tests.factories import create_payment_created_outbox


def test_payment_created_message_from_outbox_returns_message_dto() -> None:
    outbox = create_payment_created_outbox()

    message = payment_created_message_from_outbox(outbox)

    assert str(message.payment_id) == outbox.payload["payment_id"]
    assert str(message.amount) == outbox.payload["amount"]
    assert message.currency == Currency.RUB
    assert str(message.webhook_url) == outbox.payload["webhook_url"]


def test_payment_created_message_from_outbox_raises_validation_error_when_payload_invalid() -> None:
    outbox = create_payment_created_outbox()
    outbox.payload = {"payment_id": "invalid-uuid"}

    with pytest.raises(ValidationError):
        payment_created_message_from_outbox(outbox)


def test_payment_created_message_to_payload_returns_json_payload() -> None:
    outbox = create_payment_created_outbox()
    message = payment_created_message_from_outbox(outbox)

    payload = payment_created_message_to_payload(message)

    assert payload == {
        "payment_id": str(message.payment_id),
        "amount": str(message.amount),
        "currency": message.currency.value,
        "webhook_url": str(message.webhook_url),
    }
