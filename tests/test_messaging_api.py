import pytest

pytest.importorskip("frcm")
httpx = pytest.importorskip("httpx")

from fastapi import FastAPI

from app.api.messaging import router


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.anyio
async def test_publish_fire_risk_returns_message_details(app: FastAPI, monkeypatch):
    class FakeMessagingService:
        def publish_for_location(self, lat: float, lon: float, points: int):
            assert lat == 60.3913
            assert lon == 5.3221
            assert points == 3
            return {
                "message_id": "message-123",
                "event": {
                    "event_type": "fire_risk_updated",
                    "location": {"lat": lat, "lon": lon},
                },
            }

    monkeypatch.setattr("app.api.messaging.FireRiskMessagingService", FakeMessagingService)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/messaging/publish-fire-risk",
            params={"lat": 60.3913, "lon": 5.3221, "points": 3},
        )

    assert response.status_code == 200
    assert response.json()["message_id"] == "message-123"
