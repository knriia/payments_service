import pytest

from payments.application.interfaces.event_publisher import IEventPublisher
from payments.application.message.message_mappers import payment_created_message_from_outbox
from payments.application.outbox_publisher_service import OutboxPublisherService
from payments.application.tests.fakes import FakeOutboxRepository, FakeUnitOfWork
from payments.domain.value_objects import OutboxEventType
from payments.tests.factories import create_payment_created_outbox


class FakeEventPublisher(IEventPublisher):
    def __init__(self) -> None:
        self.published: list[tuple[OutboxEventType, object]] = []

    async def publish(self, event_type: OutboxEventType, payload: object) -> None:
        self.published.append((event_type, payload))


@pytest.mark.asyncio
async def test_publish_pending_publishes_unpublished_outbox_and_marks_as_published() -> None:
    uow = FakeUnitOfWork()
    outbox_repo = FakeOutboxRepository()
    event_publisher = FakeEventPublisher()
    service = OutboxPublisherService(
        uow=uow,
        outbox_repo=outbox_repo,
        event_publisher=event_publisher,
    )
    outbox = create_payment_created_outbox()
    outbox_repo.outbox_records.append(outbox)

    published_count = await service.publish_pending(limit=10)

    assert published_count == 1
    assert len(event_publisher.published) == 1
    event_type, message = event_publisher.published[0]
    assert event_type == outbox.event_type
    assert message == payment_created_message_from_outbox(outbox)
    assert outbox.published_at is not None
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_publish_pending_respects_limit() -> None:
    uow = FakeUnitOfWork()
    outbox_repo = FakeOutboxRepository()
    event_publisher = FakeEventPublisher()
    service = OutboxPublisherService(
        uow=uow,
        outbox_repo=outbox_repo,
        event_publisher=event_publisher,
    )
    first_outbox = create_payment_created_outbox()
    second_outbox = create_payment_created_outbox()
    outbox_repo.outbox_records.extend([first_outbox, second_outbox])

    published_count = await service.publish_pending(limit=1)

    assert published_count == 1
    assert len(event_publisher.published) == 1
    assert first_outbox.published_at is not None
    assert second_outbox.published_at is None
    assert uow.committed is True


@pytest.mark.asyncio
async def test_publish_pending_commits_when_no_unpublished_records() -> None:
    uow = FakeUnitOfWork()
    outbox_repo = FakeOutboxRepository()
    event_publisher = FakeEventPublisher()
    service = OutboxPublisherService(
        uow=uow,
        outbox_repo=outbox_repo,
        event_publisher=event_publisher,
    )

    published_count = await service.publish_pending(limit=10)

    assert published_count == 0
    assert event_publisher.published == []
    assert uow.committed is True
    assert uow.rolled_back is False
