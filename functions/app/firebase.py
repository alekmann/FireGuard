import os
import firebase_admin
from firebase_admin import credentials


def init_firebase():
    if os.getenv("DISABLE_FIREBASE") == "true":
        return

    if firebase_admin._apps:
        return

    # Emulator (lokalt)
    if os.getenv("FIREBASE_AUTH_EMULATOR_HOST"):
        firebase_admin.initialize_app()
        return

    # Produksjon (Firebase Cloud Functions / Cloud Run)
    # Bruker Application Default Credentials automatisk
    if os.getenv("K_SERVICE"):
        firebase_admin.initialize_app()
        return

    # Lokalt / CI med service account
    path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not path:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT is required for local development"
        )

    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
