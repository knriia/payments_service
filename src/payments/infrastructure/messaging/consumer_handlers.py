from dishka_faststream import FromDishka, inject
from faststream.rabbit import RabbitRouter

from core.messaging.events import payments_new_queue
from payments.application.message.message_dto import PaymentCreatedMessageDTO
from payments.application.payment_service import PaymentService

router = RabbitRouter()


@router.subscriber(payments_new_queue)
@inject
async def handle_payment_created(
    message: PaymentCreatedMessageDTO,
    service: FromDishka[PaymentService],
) -> None:
    await service.process_payment(payment_id=message.payment_id)
