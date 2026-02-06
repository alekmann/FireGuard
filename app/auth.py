from firebase_admin import auth
from fastapi import HTTPException, status
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def verify_token(token: str):
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    - Henter Authorization: Bearer <token>
    - Trekker ut <token>
    - Kaller verify_token(token)
    """
    return verify_token(credentials.credentials)