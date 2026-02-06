from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter(prefix="/protected", tags=["protected"])

@router.get("/health")
def protected_health(user=Depends(get_current_user)):
    return {
        "status": "OK",
        "uid": user["uid"]
    }
