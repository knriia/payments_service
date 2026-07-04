from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from payments.domain.entities import Payment
from payments.domain.exceptions import InvalidStatusTransition
from payments.domain.value_objects import Currency, Money, PaymentStatus


def _create_payment() -> Payment:
    return Payment.create(
        money=Money(amount=Decimal("100"), currency=Currency.EUR),
        description="description",
        metadata={"1": 1},
        idempotency_key="idempotency_key",
        webhook_url="http://helo",
    )


def test_create_payment_sets_id() -> None:
    payment = _create_payment()
    assert isinstance(payment.id, UUID)


def test_create_payment_sets_pending_status() -> None:
    payment = _create_payment()
    assert payment.status == PaymentStatus.PENDING


def test_create_payment_sets_created_at() -> None:
    before = datetime.now(UTC)
    payment = _create_payment()
    after = datetime.now(UTC)
    assert before <= payment.created_at <= after
    assert payment.created_at.tzinfo == UTC


def test_create_payment_sets_processed_at_to_none() -> None:
    payment = _create_payment()
    assert payment.processed_at is None


def test_mark_succeeded_sets_status_and_processed_at() -> None:
    payment = _create_payment()
    processed_at = datetime.now(UTC)
    payment.mark_succeeded(processed_at)
    assert payment.status == PaymentStatus.SUCCEEDED
    assert payment.processed_at == processed_at


def test_mark_succeeded_raises_error_when_payment_already_succeeded() -> None:
    payment = _create_payment()
    processed_at = datetime.now(UTC)
    payment.mark_succeeded(processed_at)
    with pytest.raises(InvalidStatusTransition):
        payment.mark_succeeded(processed_at)


def test_mark_failed_sets_status_and_processed_at() -> None:
    payment = _create_payment()
    processed_at = datetime.now(UTC)
    payment.mark_failed(processed_at)
    assert payment.status == PaymentStatus.FAILED
    assert payment.processed_at == processed_at


def test_mark_failed_raises_error_when_payment_already_failed() -> None:
    payment = _create_payment()
    processed_at = datetime.now(UTC)
    payment.mark_failed(processed_at)
    with pytest.raises(InvalidStatusTransition):
        payment.mark_failed(processed_at)
