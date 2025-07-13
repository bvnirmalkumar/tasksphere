import asyncio
import random
from typing import Optional
from ..interfaces.Istorage import JobStatusStore
from ..interfaces.Iqueue import JobQueueInterface
from ..interfaces.Ilogger import LoggerInterface
from ..config import RETRY_LIMIT, BACKOFF_BASE, JOB_TIMEOUT

try:
    from prometheus_client import Gauge, Counter
    in_progress = Gauge("worker_jobs_in_progress", "Jobs currently being processed by worker")
    job_retry_counter = Counter("job_retries_total", "Total retries for all jobs")
except ImportError:
    in_progress = None
    job_retry_counter = None

class JobConsumer:
    """
    Enterprise-level job consumer for distributed job queue engine.
    Handles job processing, retries, logging, and metrics.
    """

    def __init__(
        self,
        store: JobStatusStore,
        queue: JobQueueInterface,
        logger: Optional[LoggerInterface] = None
    ):
        self.store = store
        self.queue = queue
        self.logger = logger

    async def process_job(
        self,
        worker_id: int,
        shutdown_event: Optional[asyncio.Event] = None
    ):
        """
        Continuously processes jobs from the queue, supports graceful shutdown,
        handles retries, updates job status, and records metrics.
        """
        while not (shutdown_event and shutdown_event.is_set()):
            try:
                job_id, job = await asyncio.wait_for(self.queue.dequeue_job(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            retries = job.get("retries", 0)
            await self.store.update_status(job_id, "IN_PROGRESS")
            if in_progress:
                in_progress.inc()
            if self.logger:
                self.logger.info(f"[Worker {worker_id}] Started job {job_id}, attempt {retries + 1}")

            try:
                await asyncio.wait_for(self.simulate_job(job_id), timeout=JOB_TIMEOUT)
                await self.store.update_status(job_id, "COMPLETED")
                if self.logger:
                    self.logger.info(f"[Worker {worker_id}] Job {job_id} completed.")
            except Exception as e:
                if retries < RETRY_LIMIT:
                    backoff = BACKOFF_BASE ** retries
                    await self.store.update_status(job_id, f"RETRY_{retries + 1}", str(e))
                    if self.logger:
                        self.logger.warning(f"[Worker {worker_id}] Job {job_id} failed: {e}. Retrying in {backoff}s.")
                    job["retries"] = retries + 1
                    if job_retry_counter:
                        job_retry_counter.inc()
                    await asyncio.sleep(backoff)
                    await self.queue.enqueue_job(job_id, job)
                else:
                    await self.store.update_status(job_id, "FAILED", str(e))
                    if self.logger:
                        self.logger.error(f"[Worker {worker_id}] Job {job_id} permanently failed.")
            finally:
                if in_progress:
                    in_progress.dec()

    async def simulate_job(self, job_id: str):
        """
        Simulates job processing. Raises an exception randomly to test retry logic.
        """
        await asyncio.sleep(random.uniform(0.5, 1.5))
        if random.random() < 0.2:
            raise Exception(f"Simulated failure for job {job_id}")
        if self.logger:
            self.logger.info(f"Simulated job {job_id} completed successfully.")