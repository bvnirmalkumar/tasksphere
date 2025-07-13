from typing import Any, Tuple, Protocol

class JobQueueInterface(Protocol):
    """
    Enterprise-grade job queue interface for dependency inversion and testability.
    Any queue implementation (in-memory, Redis, etc.) should implement these methods.
    """
    async def enqueue_job(self, job_id: str, payload: dict):
        ...

    async def dequeue_job(self) -> Tuple[str, Any]:
        ...