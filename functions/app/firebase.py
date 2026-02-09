import os
import firebase_admin


def init_firebase():
    if os.getenv("DISABLE_FIREBASE") == "true":
        return

    if firebase_admin._apps:
        return

    # Emulator
    if os.getenv("FIREBASE_AUTH_EMULATOR_HOST"):
        firebase_admin.initialize_app()
        return

    # Cloud Run / GitHub Actions / GCP
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("K_SERVICE"):
        firebase_admin.initialize_app()
        return

    raise RuntimeError("Firebase credentials not configured")

