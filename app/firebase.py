import os
import firebase_admin
from firebase_admin import credentials


def init_firebase():
    if os.getenv("DISABLE_FIREBASE") == "true":
        return

    if firebase_admin._apps:
        return

    if os.getenv("FIREBASE_AUTH_EMULATOR_HOST"):
        print("🔥 Using Firebase Auth Emulator")

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not path:
        raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT env variable")

    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
