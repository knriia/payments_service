from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from payments.application.interfaces.outbox_repository import IOutboxRepository
from payments.application.interfaces.payment_gateway import IPaymentGateway
from payments.application.interfaces.payment_repository import IPaymentRepository
from payments.application.interfaces.unit_of_work import IUnitOfWork
from payments.application.payment_service import PaymentService
from payments.infrastructure.db.repositories.outbox_repository import OutboxRepository
from payments.infrastructure.db.repositories.payment_repository import PaymentRepository
from payments.infrastructure.db.unit_of_work import UnitOfWork
from payments.infrastructure.gateway.fake_payment_gateway import FakePaymentGateway


class PaymentProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def payment_repository(self, db_session: AsyncSession) -> IPaymentRepository:
        return PaymentRepository(session=db_session)

    @provide(scope=Scope.REQUEST)
    def outbox_repository(self, db_session: AsyncSession) -> IOutboxRepository:
        return OutboxRepository(session=db_session)

    @provide(scope=Scope.REQUEST)
    def unit_of_work(self, db_session: AsyncSession) -> IUnitOfWork:
        return UnitOfWork(session=db_session)

    @provide(scope=Scope.APP)
    def fake_payment_gateway(self) -> IPaymentGateway:
        return FakePaymentGateway()

    @provide(scope=Scope.REQUEST)
    def payment_service(
        self,
        payment_repository: IPaymentRepository,
        outbox_repository: IOutboxRepository,
        unit_of_work: IUnitOfWork,
        payment_gateway: IPaymentGateway,
    ) -> PaymentService:
        return PaymentService(
            payment_repo=payment_repository,
            outbox_repo=outbox_repository,
            uow=unit_of_work,
            payment_gateway=payment_gateway,
        )
