# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
from __future__ import annotations

from fastapi import Depends, FastAPI
from firebase_admin import initialize_app
from firebase_functions import https_fn
from firebase_functions.options import set_global_options

from app.api.fire_risk import router as fire_risk_router
from app.security.api_keys import require_api_key
from app.tools.asgi_adapter import AsgiToWsgi

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)
initialize_app()

app = FastAPI(title="FireGuard API")

# Public
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "fireguard"}

# Protected routers
app.include_router(
    fire_risk_router,
    dependencies=[Depends(require_api_key)],
)

wsgi_app = AsgiToWsgi(app)

@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    status_headers: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]], exc_info=None) -> None:
        status_headers["status"] = status
        status_headers["headers"] = headers

    body_parts: list[bytes] = []
    try:
        result = wsgi_app(req.environ, start_response)
        for chunk in result:
            body_parts.append(chunk)
    except Exception as exc:  # pragma: no cover - diagnostic logging for emulator failures
        import traceback

        traceback.print_exc()
        return https_fn.Response(f"Adapter error: {exc}", status=500)
    finally:
        if "result" in locals() and hasattr(result, "close"):
            result.close()

    status_code = int(str(status_headers.get("status", "200")).split(" ", 1)[0])
    headers = dict(status_headers.get("headers", []))
    return https_fn.Response(b"".join(body_parts), status=status_code, headers=headers)