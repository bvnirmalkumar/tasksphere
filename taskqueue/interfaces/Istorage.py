from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class JobStatusStore(ABC):
    """
    Enterprise-grade job status store interface for dependency inversion and testability.
    Any storage implementation (in-memory, Redis, database, etc.) should implement these methods.
    """

    @abstractmethod
    async def add_job(self, job: Dict[str, Any]) -> None:
        """
        Add a new job to the store.
        """
        pass

    @abstractmethod
    async def update_status(self, job_id: str, status: str, error: Optional[str] = None) -> None:
        """
        Update the status (and optionally error) of a job.
        """
        pass

    @abstractmethod
    async def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the status and metadata of a job by its ID.
        """
        pass

    @abstractmethod
    async def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all jobs and their metadata from the store.
        """
        pass