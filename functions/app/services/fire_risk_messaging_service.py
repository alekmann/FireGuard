from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from firebase_admin import firestore

from MET_client import fetch_weather_records_for_location
from app.services.fire_risk_service import compute_fire_risk_from_records
from app.services.pubsub_publisher_service import PubSubPublisherService


EVENT_LOG_COLLECTION = "fire_risk_event_log"


class FireRiskMessagingService:
    def __init__(self, publisher: PubSubPublisherService | None = None) -> None:
        self.publisher = publisher or PubSubPublisherService()
        self.db = firestore.client()

    def build_event_payload(
        self,
        lat: float,
        lon: float,
        points: int,
        records: list[dict[str, Any]],
        result: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_id": str(uuid4()),
            "event_type": "fire_risk_updated",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "location": {"lat": lat, "lon": lon},
            "points": points,
            "forecast_start": records[0]["timestamp"],
            "forecast_end": records[-1]["timestamp"],
            "ttf": result.get("ttf"),
            "result": result,
        }

    def log_event(self, payload: dict[str, Any], message_id: str) -> None:
        self.db.collection(EVENT_LOG_COLLECTION).document(payload["event_id"]).set(
            {
                "message_id": message_id,
                "payload": payload,
            }
        )

    def publish_for_location(self, lat: float, lon: float, points: int = 12) -> dict[str, Any]:
        records = fetch_weather_records_for_location(lat=lat, lon=lon, max_points=points)
        result = compute_fire_risk_from_records(records)
        payload = self.build_event_payload(
            lat=lat,
            lon=lon,
            points=points,
            records=records,
            result=result,
        )
        message_id = self.publisher.publish_json(payload)
        self.log_event(payload, message_id)

        return {
            "message_id": message_id,
            "event": payload,
        }
