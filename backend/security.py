"""Security middleware: correlation ID, rate-limit shim, CORS, security headers."""
from __future__ import annotations
import time
import uuid
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Ensures every request has a correlation ID."""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        corr = request.headers.get("x-correlation-id") or uuid.uuid4().hex[:16]
        request.state.correlation_id = corr
        response = await call_next(request)
        response.headers["x-correlation-id"] = corr
        return response


class RateLimitShim(BaseHTTPMiddleware):
    """Simple in-memory rate limiter by role and route prefix."""
    def __init__(self, app, limits: dict | None = None):
        super().__init__(app)
        self._limits = limits or {"*": 100, "beneficiary": 60, "officer": 120}
        self._buckets: dict = defaultdict(lambda: {"count": 0, "reset": time.time() + 60})

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        role = request.headers.get("x-sanad-role", "beneficiary")
        limit = self._limits.get(role, self._limits["*"])
        now = time.time()
        bucket = self._buckets[f"{role}:{request.url.path}"]
        if now > bucket["reset"]:
            bucket["count"] = 0
            bucket["reset"] = now + 60
        bucket["count"] += 1
        if bucket["count"] > limit:
            return Response(status_code=429, content='{"error_code":"RATE_LIMITED","message":"Too many requests"}', media_type="application/json")
        return await call_next(request)


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers[k] = v
        return response


REQUEST_SIZE_LIMIT = 1_000_000  # 1MB


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > REQUEST_SIZE_LIMIT:
            return Response(status_code=413, content='{"error_code":"PAYLOAD_TOO_LARGE","message":"Request exceeds 1MB limit"}', media_type="application/json")
        return await call_next(request)
