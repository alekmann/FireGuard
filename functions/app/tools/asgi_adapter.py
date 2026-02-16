from asgiref.sync import async_to_sync
from typing import Callable, Iterable


class AsgiToWsgi:
    """Minimal ASGI -> WSGI adapter so FastAPI can run under firebase_functions."""

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    def __call__(self, environ, start_response: Callable[[str, list[tuple[str, str]]], None]) -> Iterable[bytes]:
        # Read only declared bytes to avoid blocking if CONTENT_LENGTH is missing.
        content_length = int(environ.get("CONTENT_LENGTH") or "0")
        body = environ["wsgi.input"].read(content_length) if content_length else b""

        headers: list[tuple[bytes, bytes]] = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                name = key[5:].replace("_", "-").lower().encode()
                headers.append((name, str(value).encode()))
        if "CONTENT_TYPE" in environ:
            headers.append((b"content-type", environ["CONTENT_TYPE"].encode()))
        if "CONTENT_LENGTH" in environ:
            headers.append((b"content-length", environ["CONTENT_LENGTH"].encode()))

        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": environ.get("REQUEST_METHOD", "GET"),
            "path": environ.get("PATH_INFO", ""),
            "raw_path": environ.get("RAW_URI", environ.get("PATH_INFO", "")).encode(),
            "root_path": environ.get("SCRIPT_NAME", ""),
            "query_string": environ.get("QUERY_STRING", "").encode(),
            "headers": headers,
            "scheme": environ.get("wsgi.url_scheme", "http"),
            "server": (environ.get("SERVER_NAME", "localhost"), int(environ.get("SERVER_PORT", "80"))),
            "client": None,
        }

        response_body: list[bytes] = []
        status_headers: dict[str, object] = {}

        async def receive():
            nonlocal body
            data, body = body, b""
            return {"type": "http.request", "body": data, "more_body": False}

        async def send(message):
            if message["type"] == "http.response.start":
                status_headers["status"] = message["status"]
                status_headers["headers"] = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.append(message.get("body", b""))

        try:
            async_to_sync(self.asgi_app)(scope, receive, send)
        except Exception as exc:  # pragma: no cover - diagnostic logging for emulator failures
            import traceback

            traceback.print_exc()
            status_headers["status"] = 500
            status_headers["headers"] = [(b"content-type", b"text/plain")]
            response_body.append(f"ASGI error: {exc}".encode())

        status_code = int(status_headers.get("status", 200))
        header_list = [
            (name.decode("latin1"), value.decode("latin1")) for name, value in status_headers.get("headers", [])
        ]
        start_response(f"{status_code} OK", header_list)
        return response_body
