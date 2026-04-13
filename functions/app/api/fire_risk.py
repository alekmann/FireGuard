from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request

from MET_client import fetch_weather_records_for_location
from app.services.fire_risk_service import compute_fire_risk_from_csv, compute_fire_risk_from_records
from app.services.fire_risk_cache_service import FireRiskCacheService

router = APIRouter(prefix="/fire-risk", tags=["fire-risk"])


JSON_REQUEST_EXAMPLE = {
    "records": [
        {
            "timestamp": "2026-04-13T12:00:00Z",
            "temperature": 16.4,
            "relative_humidity": 52.0,
            "wind_speed": 6.8,
        },
        {
            "timestamp": "2026-04-13T13:00:00Z",
            "temperature": 17.1,
            "relative_humidity": 49.0,
            "wind_speed": 7.5,
        },
    ]
}

CSV_REQUEST_EXAMPLE = """timestamp,temperature,relative_humidity,wind_speed
2026-04-13T12:00:00Z,16.4,52.0,6.8
2026-04-13T13:00:00Z,17.1,49.0,7.5
"""

FIRE_RISK_RESPONSE_EXAMPLE = {
    "ttf": [37.2, 35.8],
    "result": {
        "firerisks": [
            {
                "ttf": 37.2,
                "temperature": 16.4,
                "humidity": 52.0,
                "wind_speed": 6.8,
            }
        ]
    },
}


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("weather", "weather_data", "records", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("JSON body must be a list or contain one of: weather, weather_data, records, data")


@router.post(
    "/compute",
    summary="Compute fire risk from weather records",
    description=(
        "Accepts either JSON records or CSV payload with fields "
        "timestamp, temperature, relative_humidity, wind_speed."
    ),
    responses={
        200: {
            "description": "Computed fire risk",
            "content": {"application/json": {"example": FIRE_RISK_RESPONSE_EXAMPLE}},
        },
        400: {"description": "Invalid input"},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "weather-records": {
                            "summary": "JSON weather records",
                            "value": JSON_REQUEST_EXAMPLE,
                        }
                    }
                },
                "text/csv": {
                    "example": CSV_REQUEST_EXAMPLE,
                },
            }
        }
    },
)
async def compute_fire_risk(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()

    try:
        if "text/csv" in content_type:
            csv_body = (await request.body()).decode("utf-8")
            return compute_fire_risk_from_csv(csv_body)

        try:
            payload = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}") from exc

        records = _extract_records(payload)
        return compute_fire_risk_from_records(records)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/compute-by-location",
    summary="Compute fire risk by geographic location",
    responses={
        200: {
            "description": "Computed fire risk",
            "content": {"application/json": {"example": FIRE_RISK_RESPONSE_EXAMPLE}},
        },
        400: {"description": "Invalid query parameters"},
        502: {"description": "Upstream weather service error"},
    },
)
async def compute_fire_risk_by_location(
    lat: float = Query(..., description="Latitude", examples=[60.3913]),
    lon: float = Query(..., description="Longitude", examples=[5.3221]),
    points: int = Query(default=12, ge=1, le=72, description="Number of hourly points", examples=[12]),
) -> dict[str, Any]:
    
    if points < 1 or points > 72:
        raise HTTPException(status_code=400, detail="points must be between 1 and 72")

    cache = FireRiskCacheService()
    cached_result = cache.get_cached_risk(lat, lon, points)
    if cached_result is not None:
        return cached_result
    
    try:
        records = fetch_weather_records_for_location(lat=lat, lon=lon, max_points=points)
        result =  compute_fire_risk_from_records(records)
        cache.save_to_cache(lat, lon, points, result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
