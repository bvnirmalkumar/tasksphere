from fastapi.testclient import TestClient
from taskqueue.api.monitor import app

client = TestClient(app)

def test_health():
    """
    Test the /health endpoint for service liveness and readiness.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "redis" in data
    assert "queue_size" in data

def test_submit_and_status():
    """
    Test job submission and status retrieval endpoints.
    """
    payload = {"task": "test_task", "parameters": {"foo": "bar"}}
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 201
    assert "job_id" in response.json()
    job_id = response.json()["job_id"]

    # Check job status
    status_response = client.get(f"/api/v1/jobs/{job_id}")
    assert status_response.status_code == 200
    status_json = status_response.json()
    assert status_json["job_id"] == job_id
    assert status_json["status"] in {
        "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED",
        "RETRY_1", "RETRY_2", "RETRY_3"
    }

def test_get_all_jobs():
    """
    Test retrieval of all jobs.
    """
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, dict)