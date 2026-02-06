from app.auth import verify_token

def test_verify_token_mocked(monkeypatch):
    def mock_verify(token):
        return {"uid": "test-user"}

    monkeypatch.setattr(
        "firebase_admin.auth.verify_id_token",
        mock_verify
    )

    decoded = verify_token("fake-token")
    assert decoded["uid"] == "test-user"
