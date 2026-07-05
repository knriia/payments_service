from datetime import UTC, datetime
from uuid import UUID

import pytest

from payments.domain.entities.outbox_entity import OutboxEntity
from payments.domain.exceptions import OutboxAlreadyPublished
from payments.domain.value_objects import OutboxEventType


def _create_outbox() -> OutboxEntity:
    return OutboxEntity.create(payload={"1": 1})


def test_create_outbox_sets_id() -> None:
    outbox = _create_outbox()
    assert isinstance(outbox.id, UUID)


def test_create_outbox_sets_event_type() -> None:
    outbox = _create_outbox()
    assert outbox.event_type == OutboxEventType.PAYMENT_CREATED


def test_create_outbox_sets_published_at_to_none() -> None:
    outbox = _create_outbox()
    assert outbox.published_at is None


def test_create_outbox_sets_created_at() -> None:
    before = datetime.now(UTC)
    outbox = _create_outbox()
    after = datetime.now(UTC)
    assert before <= outbox.created_at <= after
    assert outbox.created_at.tzinfo == UTC


def test_mark_published_sets_published_at() -> None:
    outbox = _create_outbox()
    published_at = datetime.now(UTC)
    outbox.mark_published(published_at)
    assert outbox.published_at == published_at


def test_mark_published_raises_error_when_outbox_already_published() -> None:
    outbox = _create_outbox()
    published_at = datetime.now(UTC)
    outbox.mark_published(published_at)
    with pytest.raises(OutboxAlreadyPublished):
        outbox.mark_published(published_at)
