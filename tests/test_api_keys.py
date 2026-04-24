import pytest
from fastapi import HTTPException

from app.security import api_keys


class FakeSnapshot:
    def __init__(self, exists, data=None):
        self.exists = exists
        self._data = data or {}

    def to_dict(self):
        return self._data


class FakeDocumentReference:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def get(self):
        return self._snapshot


class FakeCollectionReference:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def document(self, _document_id):
        return FakeDocumentReference(self._snapshot)


class FakeFirestoreClient:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def collection(self, _collection_name):
        return FakeCollectionReference(self._snapshot)


def test_require_api_key_missing_header_returns_401():
    with pytest.raises(HTTPException) as exc_info:
        api_keys.require_api_key(None)

    assert exc_info.value.status_code == 401
    assert "Missing X-API-Key" in exc_info.value.detail


def test_require_api_key_revoked_key_returns_403(monkeypatch):
    revoked_snapshot = FakeSnapshot(exists=True, data={"revoked": True})
    fake_client = FakeFirestoreClient(snapshot=revoked_snapshot)
    monkeypatch.setattr("app.security.api_keys.firestore.client", lambda: fake_client)

    with pytest.raises(HTTPException) as exc_info:
        api_keys.require_api_key("FGK_revoked")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "API key revoked"
