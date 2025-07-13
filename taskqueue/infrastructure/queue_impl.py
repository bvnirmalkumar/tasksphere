import asyncio
from typing import Any, Tuple
from ..interfaces.Iqueue import JobQueueInterface
import json

class InMemoryJobQueue(JobQueueInterface):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._queue = asyncio.Queue()
        return cls._instance

    async def enqueue_job(self, job_id: str, payload: dict):
        await self._queue.put((job_id, payload))

    async def dequeue_job(self) -> Tuple[str, Any]:
        return await self._queue.get()

# Redis-based implementation
try:
    import redis.asyncio as redis
    from taskqueue.config import REDIS_HOST, REDIS_PORT

    QUEUE_NAME = "job_queue"
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    class RedisJobQueue(JobQueueInterface):
        QUEUE_NAME = QUEUE_NAME

        def __init__(self):
            self.redis_client = redis_client

        async def enqueue_job(self, job_id: str, payload: dict):
            job = payload.copy()
            job["job_id"] = job_id
            await self.redis_client.lpush(self.QUEUE_NAME, json.dumps(job))

        async def dequeue_job(self) -> Tuple[str, Any]:
            _, job_data = await self.redis_client.brpop(self.QUEUE_NAME)
            job = json.loads(job_data)
            return job["job_id"], job

    async def get_redis_queue_length():
        return await redis_client.llen(QUEUE_NAME)

except ImportError:
    RedisJobQueue = None
    redis_client = None
    QUEUE_NAME = None
    async def get_redis_queue_length():
        return None