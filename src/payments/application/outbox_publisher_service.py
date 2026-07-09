from core.logging import get_logger
from payments.application.interfaces.event_publisher import IEventPublisher
from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.application.interfaces.unit_of_work import IUnitOfWork
from payments.application.message.message_mappers import payment_created_message_from_outbox

logger = get_logger(__name__)


class OutboxPublisherService:
    def __init__(
        self,
        uow: IUnitOfWork,
        outbox_repo: IOutboxRepository,
        event_publisher: IEventPublisher,
    ):
        self.uow = uow
        self.outbox_repo = outbox_repo
        self.event_publisher = event_publisher

    async def publish_pending(self, limit: int) -> int:
        async with self.uow:
            outbox_records = await self.outbox_repo.list_unpublished(limit=limit)

            for outbox in outbox_records:
                try:
                    message = payment_created_message_from_outbox(outbox)
                    await self.event_publisher.publish(event_type=outbox.event_type, payload=message)
                    logger.info(
                        "Outbox message published: outbox_id=%s event_type=%s payment_id=%s",
                        outbox.id,
                        outbox.event_type,
                        message.payment_id,
                    )
                    await self.outbox_repo.mark_as_published(outbox_id=outbox.id)
                except Exception:
                    logger.exception(
                        "Outbox message publishing failed: outbox_id=%s event_type=%s",
                        outbox.id,
                        outbox.event_type,
                    )
                    raise

            await self.uow.commit()

        return len(outbox_records)
