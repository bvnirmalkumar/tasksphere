import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
WORKER_COUNT = int(os.getenv("WORKER_COUNT", 3))
RETRY_LIMIT = int(os.getenv("RETRY_LIMIT", 3))
BACKOFF_BASE = int(os.getenv("BACKOFF_BASE", 2))
JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", 5))