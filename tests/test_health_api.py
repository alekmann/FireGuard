from fastapi.testclient import TestClient
from app.main import app

def test_protected_health(monkeypatch):
    def mock_verify(token):
        return {"uid": "test-user"}

    monkeypatch.setattr(
        "app.api.health.verify_token",
        mock_verify
    )

    client = TestClient(app)

    response = client.get(
        "/protected/health",
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
