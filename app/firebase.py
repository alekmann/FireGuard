import os
import firebase_admin
from firebase_admin import credentials
import os

if os.getenv("FIREBASE_AUTH_EMULATOR_HOST"):
    print("🔥 Using Firebase Auth Emulator")


def init_firebase():
    if firebase_admin._apps:
        return

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not path:
        raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT env variable")

    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
