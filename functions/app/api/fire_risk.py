from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from MET_client import fetch_weather_records_for_location
from app.services.fire_risk_service import compute_fire_risk_from_csv, compute_fire_risk_from_records

router = APIRouter(prefix="/fire-risk", tags=["fire-risk"])


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("weather", "weather_data", "records", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("JSON body must be a list or contain one of: weather, weather_data, records, data")


@router.post("/compute")
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


@router.get("/compute-by-location")
async def compute_fire_risk_by_location(lat: float, lon: float, points: int = 12) -> dict[str, Any]:
    if points < 1 or points > 72:
        raise HTTPException(status_code=400, detail="points must be between 1 and 72")

    try:
        records = fetch_weather_records_for_location(lat=lat, lon=lon, max_points=points)
        return compute_fire_risk_from_records(records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
