from __future__ import annotations

import json
from typing import Any

from firebase_admin import get_app


DEFAULT_PROJECT_ID = "fireguard-2faea"
PUBSUB_TOPIC_ID = "fire-risk-updated"


def _resolve_project_id() -> str:
    try:
        app = get_app()
    except ValueError:
        return DEFAULT_PROJECT_ID

    project_id = getattr(app, "project_id", None)
    if project_id:
        return project_id

    options = getattr(app, "options", {}) or {}
    return options.get("projectId") or options.get("project_id") or DEFAULT_PROJECT_ID


class PubSubPublisherService:
    def __init__(self, project_id: str | None = None, topic_id: str | None = None) -> None:
        self.project_id = project_id or _resolve_project_id()
        self.topic_id = topic_id or PUBSUB_TOPIC_ID

    def is_configured(self) -> bool:
        return bool(self.project_id and self.topic_id)

    def publish_json(self, payload: dict[str, Any]) -> str:
        if not self.is_configured():
            raise RuntimeError("Pub/Sub is not configured.")

        from google.cloud import pubsub_v1

        publisher = pubsub_v1.PublisherClient()
        try:
            topic_path = publisher.topic_path(self.project_id, self.topic_id)
            future = publisher.publish(
                topic_path,
                json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            )
            return future.result(timeout=10)
        finally:
            publisher.stop()
