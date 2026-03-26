from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.fire_risk_messaging_service import FireRiskMessagingService


router = APIRouter(prefix="/messaging", tags=["messaging"])

@router.post("/publish-fire-risk")
async def publish_fire_risk(
    lat: float = Query(...),
    lon: float = Query(...),
    points: int = Query(default=12, ge=1, le=72),
) -> dict:
    try:
        service = FireRiskMessagingService()
        return service.publish_for_location(
            lat=lat,
            lon=lon,
            points=points,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
