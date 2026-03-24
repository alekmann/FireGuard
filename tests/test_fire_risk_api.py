import pytest

pytest.importorskip("frcm")
httpx = pytest.importorskip("httpx")

from fastapi import FastAPI

from app.api.fire_risk import router


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.anyio
async def test_compute_by_location_returns_cached_result(app: FastAPI, monkeypatch):
    cached_response = {"ttf": [12.5], "result": {"source": "cache"}}

    class FakeCacheService:
        def get_cached_risk(self, lat: float, lon: float, points: int):
            assert lat == 59.9123
            assert lon == 10.7543
            assert points == 12
            return cached_response

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Weather fetch should not run on cache hit")

    monkeypatch.setattr("app.api.fire_risk.FireRiskCacheService", FakeCacheService)
    monkeypatch.setattr("app.api.fire_risk.fetch_weather_records_for_location", fail_if_called)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/fire-risk/compute-by-location",
            params={"lat": 59.9123, "lon": 10.7543, "points": 12},
        )

    assert response.status_code == 200
    assert response.json() == cached_response
