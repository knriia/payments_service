from dishka_faststream import setup_dishka
from faststream import FastStream

from core.config import Settings
from core.messaging.broker import create_broker
from entrypoints.container import create_container
from payments.infrastructure.messaging.consumer_handlers import router


def create_app() -> FastStream:
    container = create_container()
    broker = create_broker(settings=Settings())
    broker.include_router(router)

    app = FastStream(broker)
    setup_dishka(container, app)

    return app


app = create_app()
