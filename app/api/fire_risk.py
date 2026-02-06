from fastapi import APIRouter, HTTPException
from app.services.fire_risk_service import FireRiskService

router = APIRouter(prefix="/fire-risk", tags=["fire-risk"])

@router.get("/sample")
def get_sample_fire_risk():
    """Get fire risk prediction using Bergen sample data."""
    try:
        prediction = FireRiskService.compute_sample_data()
        
        # Convert to a more JSON-friendly format
        results = []
        for risk in prediction.firerisks:
            results.append({
                "timestamp": risk.timestamp.isoformat(),
                "time_to_flashover": risk.ttf,
                "risk_level": "high" if risk.ttf < 3 else "medium" if risk.ttf < 6 else "low"
            })
        
        return {
            "status": "success",
            "location": "Bergen, Norway",
            "data_points": len(results),
            "predictions": results[:10],  # First 10 for demo
            "summary": {
                "min_ttf": min(r["time_to_flashover"] for r in results),
                "max_ttf": max(r["time_to_flashover"] for r in results), 
                "avg_ttf": sum(r["time_to_flashover"] for r in results) / len(results)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fire risk computation failed: {str(e)}")

@router.get("/health")
def fire_risk_health():
    """Health check for fire risk service."""
    try:
        # Test that we can access the sample data
        sample_path = FireRiskService.get_sample_data_path()
        if not sample_path.exists():
            raise HTTPException(status_code=500, detail="Sample data file not found")
        
        return {
            "status": "healthy",
            "service": "fire-risk-computation", 
            "sample_data": str(sample_path),
            "data_exists": sample_path.exists()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")