from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.fire_risk_messaging_service import FireRiskMessagingService


router = APIRouter(prefix="/messaging", tags=["messaging"])


PUBLISH_RESPONSE_EXAMPLE = {
    "status": "published",
    "topic": "fire-risk",
    "message_id": "1713026600123456",
    "lat": 60.3913,
    "lon": 5.3221,
    "points": 12,
}

@router.post(
    "/publish-fire-risk",
    summary="Publish fire risk message",
    responses={
        200: {
            "description": "Message published",
            "content": {"application/json": {"example": PUBLISH_RESPONSE_EXAMPLE}},
        },
        400: {"description": "Invalid query parameters"},
        502: {"description": "Publishing failed"},
    },
)
async def publish_fire_risk(
    lat: float = Query(..., description="Latitude", examples=[60.3913]),
    lon: float = Query(..., description="Longitude", examples=[5.3221]),
    points: int = Query(default=12, ge=1, le=72, description="Number of hourly points", examples=[12]),
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
