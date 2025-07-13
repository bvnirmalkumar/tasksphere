"""
Enterprise-level FastAPI application for monitoring and interacting with the distributed job queue engine.
"""

import asyncio
from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
from prometheus_client import Counter, Gauge, generate_latest

from ..infrastructure.storage_impl import InMemoryJobStatusStore
from ..infrastructure.queue_impl import InMemoryJobQueue, redis_client, QUEUE_NAME, get_redis_queue_length
from ..core.producer import JobProducer
from ..core.consumer import JobConsumer



# Create the FastAPI app and include the router
app = FastAPI(
    title="Distributed Job Queue Engine API",
    version="1.0.0",
    description="Production API for distributed job queue management and monitoring."
)
# Versioned API router for scalability and future-proofing
router = APIRouter(
    prefix="/api/v1"
)

jobs_submitted = Counter("jobs_submitted_total", "Total jobs submitted")
jobs_completed = Counter("jobs_completed_total", "Total jobs completed")
jobs_failed = Counter("jobs_failed_total", "Total jobs failed")
current_jobs = Gauge("jobs_in_progress", "Jobs currently being processed")

job_status_store = InMemoryJobStatusStore()
job_queue = InMemoryJobQueue()
job_producer = JobProducer(job_status_store, job_queue)
job_consumer = JobConsumer(job_status_store, job_queue)

@app.on_event("startup")
async def startup_all():
    # Start workers
    for worker_id in range(3):
        asyncio.create_task(job_consumer.process_job(worker_id))

@router.get(
    "/health",
    tags=["Health"],
    summary="Liveness/Readiness Probe",
    response_model=Dict[str, Any],
    response_description="Service health and Redis queue status"
)
async def health_check():
    """
    Health check endpoint for Docker/Kubernetes liveness/readiness probes,
    load balancers, CI pipelines, and monitoring tools.
    Returns HTTP 200 OK with {"status": "ok"} and Redis queue size if available.
    """
    queue_size = None
    redis_status = "unavailable"
    if redis_client and QUEUE_NAME:
        try:
            queue_size = await get_redis_queue_length()
            redis_status = "connected"
        except Exception:
            redis_status = "error"
    return {"status": "ok", "redis": redis_status, "queue_size": queue_size}

@router.post(
    "/jobs",
    tags=["Jobs"],
    summary="Submit a new job",
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    response_description="Job submission result"
)
async def submit(payload: Dict[str, Any]):
    """
    Submits a job with the given payload to the job queue.
    """
    jobs_submitted.inc()
    job_id = await job_producer.submit_job(payload)
    return {"job_id": job_id}

@router.get(
    "/jobs/{job_id}",
    tags=["Jobs"],
    summary="Get job status",
    response_model=Dict[str, Any],
    response_description="Job status and metadata"
)
async def get_status(job_id: str):
    """
    Retrieve the status of a job by its ID.
    """
    job = await job_status_store.get_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job ID not found")
    if job.get("status") == "COMPLETED":
        jobs_completed.inc()
    elif job.get("status") == "FAILED":
        jobs_failed.inc()
    return job

@router.get(
    "/jobs",
    tags=["Jobs"],
    summary="Get all jobs",
    response_model=Dict[str, Any],
    response_description="All jobs and their metadata"
)
async def get_all_jobs():
    """
    Asynchronously retrieves all jobs from the job status store.
    """
    return await job_status_store.get_all_jobs()

@router.get(
    "/metrics",
    tags=["Metrics"],
    response_class=PlainTextResponse
)
async def metrics():
    """
    Exposes Prometheus metrics for monitoring.
    """
    return generate_latest().decode("utf-8")

app.include_router(router)