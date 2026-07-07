from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from payments.application.interfaces.payment_repository import IPaymentRepository
from payments.domain.entities.payment_entity import PaymentEntity
from payments.domain.exceptions import DuplicateIdempotencyKey
from payments.infrastructure.db.mappers.payment_mapper import (
    payment_entity_to_payment_model,
    payment_model_to_payment_entity,
)
from payments.infrastructure.db.models import PaymentModel


class PaymentRepository(IPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, payment_entity: PaymentEntity) -> None:
        payment_model = payment_entity_to_payment_model(payment_entity)
        self.session.add(payment_model)
        try:
            await self.session.flush()
        except IntegrityError as error:
            if "idempotency_key" in str(error.orig):
                raise DuplicateIdempotencyKey("Payment with this idempotency key already exists") from error
            raise

    async def get_by_id(self, payment_id: UUID) -> PaymentEntity | None:
        model = await self.session.get(PaymentModel, payment_id)
        if model is None:
            return None

        return payment_model_to_payment_entity(payment_model=model)

    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentEntity | None:
        stmt = select(PaymentModel).where(PaymentModel.idempotency_key == idempotency_key)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        return payment_model_to_payment_entity(payment_model=model)

    async def update(self, payment_entity: PaymentEntity) -> None:
        stmt = (
            update(PaymentModel)
            .where(PaymentModel.id == payment_entity.id)
            .values(
                status=payment_entity.status.value,
                processed_at=payment_entity.processed_at,
            )
        )
        await self.session.execute(stmt)
