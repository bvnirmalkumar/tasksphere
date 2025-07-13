import uuid
from typing import Dict, Any, Optional
from ..interfaces.Istorage import JobStatusStore
from ..interfaces.Iqueue import JobQueueInterface
from ..interfaces.Ilogger import LoggerInterface

class JobProducer:
    """
    Enterprise-grade job producer for distributed job queue engine.
    Handles job creation, validation, and submission to the queue.
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

    async def submit_job(self, task: Dict[str, Any]) -> str:
        """
        Submits a new job to the queue and persists its metadata.
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "task": task,
            "status": "PENDING",
            "retries": 0,
            "last_error": None
        }
        await self.store.add_job(job_data)
        await self.queue.enqueue_job(job_id, job_data)
        if self.logger:
            self.logger.info(f"Submitted job {job_id}")
        return job_id