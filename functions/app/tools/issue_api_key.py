"""
Issue a new API key for a tester.

Stores only SHA-256 hash in Firestore:
- collection: api_keys
- document id: sha256(raw_key)
- fields: name, created_at, revoked

Run:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
  python tools/issue_api_key.py --name "tester1"

Output:
  Prints the raw API key ONCE. You give it to the tester.
"""
from __future__ import annotations

import argparse
import hashlib
import secrets
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore


COLLECTION = "api_keys"
PREFIX = "FGK_"


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_key() -> str:
    # 32 bytes -> urlsafe ~43 chars, high entropy
    return PREFIX + secrets.token_urlsafe(32)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Human name for the key owner/tester")
    args = parser.parse_args()

    firebase_admin.initialize_app(credentials.ApplicationDefault())
    db = firestore.client()

    raw_key = generate_key()
    key_hash = sha256_hex(raw_key)

    doc_ref = db.collection(COLLECTION).document(key_hash)
    doc_ref.set(
        {
            "name": args.name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revoked": False,
        }
    )

    print("\n=== API KEY (give this to the tester) ===")
    print(raw_key)
    print("=== END (not stored in Firestore) ===\n")
    print(f"Stored hash doc id: {key_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
