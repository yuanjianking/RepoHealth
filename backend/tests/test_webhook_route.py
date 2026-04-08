from fastapi.testclient import TestClient

from app.main import app


def test_webhook_route_accepts_event():
    client = TestClient(app)
    payload = {
        "repository": {"full_name": "example/repo"},
        "action": "opened",
        "issue": {"number": 1},
    }
    headers = {"X-GitHub-Event": "issues"}

    response = client.post("/api/v1/webhook/webhook", json=payload, headers=headers)

    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "event queued"
    assert data["repository"] == "example/repo"
    assert data["event"] == "issues"
