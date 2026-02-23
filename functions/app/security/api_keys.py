# functions/app/security/api_keys.py
"""
API-key authentication for service-to-service use.

How it works:
- Clients send X-API-Key: <raw_key>
- Server hashes raw_key with SHA-256
- Looks up Firestore document with id == sha256(raw_key)
- If exists and not revoked -> authorized

Why:
- No UI needed
- Supports multiple testers (multiple keys)
- Firestore stores only hashes, not raw keys
"""
from __future__ import annotations

import hashlib
from typing import Optional

from fastapi import Header, HTTPException, status
from firebase_admin import firestore

API_KEY_HEADER = "X-API-Key"
COLLECTION = "api_keys"


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_api_key(x_api_key: Optional[str] = Header(default=None, alias=API_KEY_HEADER)) -> None:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing {API_KEY_HEADER}",
        )

    key_hash = _sha256_hex(x_api_key.strip())
    db = firestore.client()
    doc_ref = db.collection(COLLECTION).document(key_hash)
    snap = doc_ref.get()

    if not snap.exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    data = snap.to_dict() or {}
    if bool(data.get("revoked", False)) is True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key revoked",
        )
