import asyncio
import signal
from .consumer import JobConsumer
from ..infrastructure.storage_impl import InMemoryJobStatusStore
from ..infrastructure.queue_impl import InMemoryJobQueue  # Use implementation, not interface
from ..infrastructure.logger_impl import get_logger       # Use implementation, not interface
from ..config import WORKER_COUNT

async def main():
    """
    Enterprise-grade runner for distributed job queue engine.
    Initializes dependencies, starts worker pool, and handles graceful shutdown.
    """
    shutdown_event = asyncio.Event()
    store = InMemoryJobStatusStore()
    queue = InMemoryJobQueue()
    logger = get_logger("JobConsumer")
    consumer = JobConsumer(store, queue, logger=logger)

    def shutdown():
        logger.info("Shutdown signal received.")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except NotImplementedError:
            # Signal handlers may not be available on some platforms (e.g., Windows)
            pass

    async def worker(worker_id):
        await consumer.process_job(worker_id, shutdown_event)

    workers = [asyncio.create_task(worker(i)) for i in range(WORKER_COUNT)]
    logger.info(f"Worker pool started with {WORKER_COUNT} workers.")
    await asyncio.wait(workers)

if __name__ == "__main__":
    asyncio.run(main())