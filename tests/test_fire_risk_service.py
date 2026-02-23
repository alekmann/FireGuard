import pytest

pytest.importorskip("frcm")

from app.services import fire_risk_service


def test_compute_fire_risk_from_records_returns_ttf_and_result(monkeypatch):
    def fake_compute(weather_data):
        assert len(weather_data.data) == 1
        return {"ttf": 42.0, "status": "ok"}

    monkeypatch.setattr(fire_risk_service, "compute", fake_compute)

    payload = [
        {
            "timestamp": "2026-02-23T12:00:00Z",
            "temperature": 20.5,
            "relative_humidity": 55.0,
            "wind_speed": 3.2,
        }
    ]

    result = fire_risk_service.compute_fire_risk_from_records(payload)

    assert result["ttf"] == 42.0
    assert result["result"]["status"] == "ok"


def test_compute_fire_risk_from_csv_parses_rows(monkeypatch):
    def fake_compute(weather_data):
        assert len(weather_data.data) == 2
        return {"ttf": 15.5}

    monkeypatch.setattr(fire_risk_service, "compute", fake_compute)

    csv_payload = (
        "timestamp,temperature,relative_humidity,wind_speed\n"
        "2026-02-23T12:00:00Z,20.5,55.0,3.2\n"
        "2026-02-23T13:00:00Z,21.0,53.0,4.0\n"
    )

    result = fire_risk_service.compute_fire_risk_from_csv(csv_payload)

    assert result["ttf"] == 15.5


def test_compute_fire_risk_from_records_missing_field_raises():
    payload = [
        {
            "timestamp": "2026-02-23T12:00:00Z",
            "temperature": 20.5,
            "wind_speed": 3.2,
        }
    ]

    with pytest.raises(ValueError, match="missing fields"):
        fire_risk_service.compute_fire_risk_from_records(payload)
