from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user

def test_protected_health():
    # 1. Fake user som dependency returnerer
    def fake_current_user():
        return {"uid": "test-user"}

    # 2. Override dependency
    app.dependency_overrides[get_current_user] = fake_current_user

    client = TestClient(app)

    # 3. Call endpoint (ingen ekte token nødvendig)
    response = client.get(
        "/protected/health",
        headers={"Authorization": "Bearer fake-token"}
    )

    # 4. Assert
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "uid": "test-user"
    }

    # 5. Cleanup (VIKTIG)
    app.dependency_overrides.clear()
