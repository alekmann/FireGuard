"""
Firebase Functions entry point for FireGuard FastAPI application.
"""

from firebase_functions import https_fn
import json

@https_fn.on_request()
def main(req: https_fn.Request) -> https_fn.Response:
    """Simple Firebase function to test deployment."""
    
    # Handle CORS
    if req.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return https_fn.Response('', status=204, headers=headers)
    
    # Import here to avoid cold start issues
    from app.services.fire_risk_service import get_bergen_sample_prediction
    
    try:
        if req.path == '/' or req.path == '/health':
            return https_fn.Response(
                json.dumps({"status": "healthy", "service": "FireGuard API"}),
                status=200,
                headers={"Content-Type": "application/json"}
            )
        
        elif req.path == '/fire-risk':
            prediction = get_bergen_sample_prediction()
            
            # Convert to JSON serializable format
            results = []
            for risk in prediction.firerisks[:10]:  # First 10 results
                results.append({
                    "timestamp": risk.timestamp.isoformat(),
                    "time_to_flashover": risk.ttf
                })
            
            response_data = {
                "status": "success",
                "location": "Bergen, Norway", 
                "predictions": results,
                "total_predictions": len(prediction.firerisks)
            }
            
            return https_fn.Response(
                json.dumps(response_data),
                status=200,
                headers={"Content-Type": "application/json"}
            )
        
        else:
            return https_fn.Response(
                json.dumps({"error": "Not found"}),
                status=404,
                headers={"Content-Type": "application/json"}
            )
            
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )