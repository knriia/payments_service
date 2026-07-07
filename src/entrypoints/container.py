from dishka import AsyncContainer, make_async_container

from core.db.di import DbProvider
from core.di import SettingsProvider
from core.messaging.di import MessagingProvider
from payments.di import PaymentProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        DbProvider(),
        MessagingProvider(),
        PaymentProvider(),
    )
