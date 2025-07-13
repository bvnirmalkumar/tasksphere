import asyncio
from typing import Dict, Any, Optional
from ..interfaces.Istorage import JobStatusStore

class InMemoryJobStatusStore(JobStatusStore):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._jobs = {}
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def add_job(self, job: Dict[str, Any]):
        async with self._lock:
            self._jobs[job["job_id"]] = job

    async def update_status(self, job_id: str, status: str, error: Optional[str] = None):
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = status
                if error:
                    job["last_error"] = error
                if "RETRY" in status:
                    job["retries"] += 1

    async def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        async with self._lock:
            return dict(self._jobs)