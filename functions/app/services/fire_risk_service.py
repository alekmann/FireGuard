from __future__ import annotations

import csv
import io
from datetime import datetime
from dataclasses import asdict, is_dataclass
from typing import Any

from frcm.datamodel.model import WeatherData, WeatherDataPoint
from frcm.fireriskmodel.compute import compute


REQUIRED_FIELDS = ("timestamp", "temperature", "relative_humidity", "wind_speed")


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp: {value}") from exc


def _to_weather_data(records: list[dict[str, Any]]) -> WeatherData:
    points: list[WeatherDataPoint] = []
    for index, record in enumerate(records):
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValueError(f"Record {index} is missing fields: {', '.join(missing)}")

        points.append(
            WeatherDataPoint(
                timestamp=_parse_timestamp(record["timestamp"]),
                temperature=float(record["temperature"]),
                humidity=float(record["relative_humidity"]),
                wind_speed=float(record["wind_speed"]),
            )
        )

    return WeatherData(data=points)


def _extract_ttf(result: Any) -> Any:
    if isinstance(result, dict):
        return result.get("ttf")
    if hasattr(result, "firerisks"):
        firerisks = getattr(result, "firerisks") or []
        return [getattr(item, "ttf", None) for item in firerisks]
    return getattr(result, "ttf", None)


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump())
    if hasattr(value, "__dict__"):
        return _to_jsonable(vars(value))
    return str(value)


def compute_fire_risk_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    weather_data = _to_weather_data(records)
    result = compute(weather_data)
    return {
        "ttf": _extract_ttf(result),
        "result": _to_jsonable(result),
    }


def compute_fire_risk_from_csv(csv_content: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(csv_content))
    records = [row for row in reader]
    if not records:
        raise ValueError("CSV input is empty")
    return compute_fire_risk_from_records(records)
