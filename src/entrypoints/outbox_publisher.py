import asyncio
import contextlib
import signal

from dishka import AsyncContainer

from entrypoints.container import create_outbox_publisher_container
from payments.application.outbox_publisher_service import OutboxPublisherService

PUBLISH_LIMIT = 100
POLL_INTERVAL_SECONDS = 2


async def run_once(container: AsyncContainer) -> int:
    async with container() as request_container:
        service = await request_container.get(OutboxPublisherService)
        return await service.publish_pending(limit=PUBLISH_LIMIT)


async def run_worker() -> None:
    stop_event = asyncio.Event()
    container = create_outbox_publisher_container()

    def request_stop() -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, request_stop)
    loop.add_signal_handler(signal.SIGINT, request_stop)

    try:
        while not stop_event.is_set():
            await run_once(container)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL_SECONDS)
    finally:
        await container.close()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
