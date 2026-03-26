import pytest

pytest.importorskip("frcm")

from app.services.fire_risk_messaging_service import FireRiskMessagingService


class FakeDocumentReference:
    def __init__(self, store, document_id):
        self.store = store
        self.document_id = document_id

    def set(self, data):
        self.store[self.document_id] = data


class FakeCollectionReference:
    def __init__(self, store):
        self.store = store

    def document(self, document_id):
        return FakeDocumentReference(self.store, document_id)


class FakeFirestoreClient:
    def __init__(self):
        self.store = {}

    def collection(self, _collection_name):
        return FakeCollectionReference(self.store)


class FakePublisher:
    def __init__(self):
        self.payloads = []

    def publish_json(self, payload):
        self.payloads.append(payload)
        return "message-123"


def test_publish_for_location_computes_and_logs_event(monkeypatch):
    fake_firestore = FakeFirestoreClient()
    fake_publisher = FakePublisher()
    records = [
        {
            "timestamp": "2026-03-25T09:00:00Z",
            "temperature": 12.0,
            "relative_humidity": 45.0,
            "wind_speed": 5.0,
        }
    ]

    monkeypatch.setattr(
        "app.services.fire_risk_messaging_service.firestore.client",
        lambda: fake_firestore,
    )
    monkeypatch.setattr(
        "app.services.fire_risk_messaging_service.fetch_weather_records_for_location",
        lambda lat, lon, max_points: records,
    )
    monkeypatch.setattr(
        "app.services.fire_risk_messaging_service.compute_fire_risk_from_records",
        lambda incoming_records: {"ttf": [4.2], "result": {"risk": "high"}},
    )

    service = FireRiskMessagingService(publisher=fake_publisher)
    outcome = service.publish_for_location(60.3913, 5.3221, 1)

    assert outcome["message_id"] == "message-123"
    assert outcome["event"]["event_type"] == "fire_risk_updated"
    assert len(fake_publisher.payloads) == 1
    assert len(fake_firestore.store) == 1
