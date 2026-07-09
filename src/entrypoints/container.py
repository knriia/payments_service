from dishka import AsyncContainer, make_async_container

from core.db.di import DbProvider
from core.di import SettingsProvider
from core.messaging.consumer_di import ConsumerProvider
from core.messaging.outbox_publisher_di import OutboxPublisherProvider
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


def create_consumer_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        PaymentProvider(),
        ConsumerProvider(),
    )
