"""
Revoke an API key.

Run:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
  python tools/revoke_api_key.py --key "FGK_...."
"""
from __future__ import annotations

import argparse
import hashlib

import firebase_admin
from firebase_admin import credentials, firestore


COLLECTION = "api_keys"


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True, help="Raw API key to revoke")
    args = parser.parse_args()

    firebase_admin.initialize_app(credentials.ApplicationDefault())
    db = firestore.client()

    key_hash = sha256_hex(args.key.strip())
    doc_ref = db.collection(COLLECTION).document(key_hash)
    snap = doc_ref.get()
    if not snap.exists:
        print("Key not found (already invalid?)")
        return 1

    doc_ref.update({"revoked": True})
    print("Revoked key hash:", key_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
