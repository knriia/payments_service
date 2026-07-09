import asyncio

from dishka_faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from core.logging import setup_logging
from entrypoints.container import create_consumer_container
from payments.infrastructure.messaging.consumer_handlers import PaymentConsumerRegistrar


async def run_consumer() -> None:
    container = create_consumer_container()
    broker = await container.get(RabbitBroker)
    registrar = await container.get(PaymentConsumerRegistrar)

    registrar.register()

    app = FastStream(broker)
    setup_dishka(container, app)

    try:
        await app.run()
    finally:
        await container.close()


def main() -> None:
    setup_logging()
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
