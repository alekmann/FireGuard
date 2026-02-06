from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.fire_risk import router as fire_risk_router

router = APIRouter()
router.include_router(health_router)
router.include_router(fire_risk_router)
