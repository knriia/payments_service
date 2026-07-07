from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, HTTPException, status

from core.security.api_key_auth import verify_api_key
from payments.application.payment_service import PaymentService
from payments.presentation.payment_dto import InputPaymentDTO, OutputPaymentDTO
from payments.presentation.payment_mappers import payment_dto_to_entity, payment_entity_to_dto

payment_router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(verify_api_key)])


@payment_router.get("/{payment_id}")
@inject
async def get_payment_by_id(payment_id: UUID, service: FromDishka[PaymentService]) -> OutputPaymentDTO:
    payment_entity = await service.get_payment_by_id(payment_id=payment_id)
    if payment_entity is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment_entity_to_dto(payment_entity=payment_entity)


@payment_router.post("", status_code=status.HTTP_202_ACCEPTED)
@inject
async def create_payment(
    payment_dto: InputPaymentDTO,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    service: FromDishka[PaymentService],
) -> OutputPaymentDTO:
    payment_entity = payment_dto_to_entity(payment_dto=payment_dto, idempotency_key=idempotency_key)
    saved_entity = await service.create_payment(payment_entity)
    return payment_entity_to_dto(payment_entity=saved_entity)
