# TaskSphere Distributed Job Queue Engine

## Overview

TaskSphere is an enterprise-ready, distributed job queue engine designed for scalable, reliable, and observable background task processing. It leverages Redis for cross-service job management, FastAPI for a robust API, and Docker for seamless deployment.

---

## Features

- Distributed job queue with Redis backend for horizontal scalability
- Asynchronous workers for high-throughput job processing
- Configurable via `.env` and `config.py`
- Prometheus metrics and health endpoints for observability
- OpenAPI documentation for all endpoints
- Dockerized architecture for easy deployment and orchestration

---

## Architecture

- **API Service:** FastAPI application for job submission, status, and monitoring
- **Worker Service:** Asynchronous workers that process jobs from the queue
- **Redis:** Centralized, persistent job queue
- **Prometheus:** Metrics endpoint for monitoring

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed

### Quick Start

```sh
docker-compose up --build
```

This command will build and start all services: Redis, API, and Worker(s).

---

## API Usage

### Submit a Job

```sh
curl -X POST http://localhost:8000/api/v1/jobs \
     -H "Content-Type: application/json" \
     -d '{"task": "demo", "parameters": {"foo": "bar"}}'
```

### Get Job Status

```sh
curl http://localhost:8000/api/v1/jobs/<job_id>
```

### List All Jobs

```sh
curl http://localhost:8000/api/v1/jobs
```

---

## Health & Metrics

- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Prometheus Metrics:** [http://localhost:8000/api/v1/metrics](http://localhost:8000/api/v1/metrics)
- **OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Configuration

All configuration is managed via environment variables and the `taskqueue/config.py` file.  
You can override defaults by creating a `.env` file in the project root.

Example `.env`:

```
REDIS_HOST=redis
REDIS_PORT=6379
WORKER_COUNT=3
RETRY_LIMIT=3
BACKOFF_BASE=2
JOB_TIMEOUT=5
```

---

## Testing

Run the test suite with:

```sh
pytest --cov=taskqueue --cov-report=term-missing
```

---

## Deployment

- Designed for container orchestration (Kubernetes, Docker Swarm, etc.)
- Resource limits and health checks are set in `docker-compose.yml`
- Easily extendable for cloud-native deployments

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

---

## License

This project is licensed under the