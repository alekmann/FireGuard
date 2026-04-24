import pytest

from app.services.pubsub_publisher_service import PubSubPublisherService


def test_publish_json_raises_when_pubsub_not_configured():
    service = PubSubPublisherService(project_id="test-project", topic_id="test-topic")
    service.project_id = ""
    service.topic_id = ""

    with pytest.raises(RuntimeError, match="Pub/Sub is not configured"):
        service.publish_json({"event": "fire_risk_updated"})
