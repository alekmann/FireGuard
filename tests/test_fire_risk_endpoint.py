import pytest

pytest.importorskip("frcm")
httpx = pytest.importorskip("httpx")

from fastapi import FastAPI

from app.api.fire_risk import router
from app.services import fire_risk_service


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.anyio
async def test_compute_endpoint_json_success(app: FastAPI, monkeypatch):
    def fake_compute(weather_data):
        assert len(weather_data.data) == 1
        return {"ttf": 7.5, "risk": "moderate"}

    monkeypatch.setattr(fire_risk_service, "compute", fake_compute)

    payload = [
        {
            "timestamp": "2026-02-23T12:00:00Z",
            "temperature": 20.5,
            "relative_humidity": 55.0,
            "wind_speed": 3.2,
        }
    ]

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/fire-risk/compute", json=payload)

    assert response.status_code == 200
    assert response.json()["ttf"] == 7.5
    assert response.json()["result"]["risk"] == "moderate"


@pytest.mark.anyio
async def test_compute_endpoint_rejects_invalid_payload(app: FastAPI):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/fire-risk/compute", json={"foo": "bar"})

    assert response.status_code == 400
    assert "JSON body must be a list" in response.json()["detail"]


@pytest.mark.anyio
async def test_compute_by_location_success(app: FastAPI, monkeypatch):
    def fake_fetch(lat: float, lon: float, max_points: int):
        assert lat == 60.3913
        assert lon == 5.3221
        assert max_points == 2
        return [
            {
                "timestamp": "2026-02-23T12:00:00Z",
                "temperature": 20.5,
                "relative_humidity": 55.0,
                "wind_speed": 3.2,
            },
            {
                "timestamp": "2026-02-23T13:00:00Z",
                "temperature": 21.0,
                "relative_humidity": 53.0,
                "wind_speed": 4.0,
            },
        ]

    def fake_compute(weather_data):
        assert len(weather_data.data) == 2
        return {"ttf": 9.1, "risk": "low"}

    monkeypatch.setattr("app.api.fire_risk.fetch_weather_records_for_location", fake_fetch)
    monkeypatch.setattr(fire_risk_service, "compute", fake_compute)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/fire-risk/compute-by-location", params={"lat": 60.3913, "lon": 5.3221, "points": 2})

    assert response.status_code == 200
    assert response.json()["ttf"] == 9.1
