import pytest

from MET_client import extract_weather_records


def test_extract_weather_records_raises_when_no_valid_points():
    raw_json = {
        "properties": {
            "timeseries": [
                {"time": "2026-01-01T00:00:00Z", "data": {}},
                {"time": "2026-01-01T01:00:00Z", "data": {"instant": {"details": {}}}},
            ]
        }
    }

    with pytest.raises(ValueError, match="No valid weather records found"):
        extract_weather_records(raw_json, max_points=2)
