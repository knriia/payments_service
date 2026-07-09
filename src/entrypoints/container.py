from dishka import AsyncContainer, make_async_container

from core.db.di import DbProvider
from core.di import SettingsProvider
from core.messaging.di import OutboxPublisherProvider
from payments.di import PaymentProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        PaymentProvider(),
    )


def create_outbox_publisher_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        OutboxPublisherProvider(),
        PaymentProvider(),
    )
