"""API middleware for auditing, rate limiting, and authentication."""
from __future__ import annotations

import time
import uuid
from datetime import datetime
from fastapi import Request, HTTPException, Header
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Callable, Dict
import logging

logger = logging.getLogger(__name__)

# Global rate limiter
limiter = Limiter(key_func=get_remote_address)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Logs all API requests and responses for compliance.

    Intentional issues for workshop:
    - Logs sensitive data (passenger info, payment details)
    - No log rotation (fills disk)
    - Synchronous logging (blocks requests)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            # Intentional: reads body, may cause issues with streaming
            body = await request.body()
            # Re-wrap body for FastAPI to read
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive

        logger.info(
            f"REQUEST {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        # Intentional: logs request body (may contain sensitive data)
        if body:
            logger.info(f"REQUEST BODY {request_id}: {body.decode('utf-8')}")

        # Process request
        try:
            response = await call_next(request)
            duration = int((time.time() - start_time) * 1000)

            logger.info(
                f"RESPONSE {request_id}: {response.status_code} "
                f"[{duration}ms]"
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            logger.error(
                f"ERROR {request_id}: {str(e)} [{duration}ms]",
                exc_info=True,
            )
            # Intentional: verbose error in response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Internal error: {str(e)}",
                    "request_id": request_id,
                    "error_type": type(e).__name__,
                },
            )


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Simple API key authentication.

    Intentional issues for workshop:
    - API keys hardcoded (no secrets management)
    - No key rotation
    - Keys transmitted in headers (not encrypted)
    - No rate limiting per key
    """

    VALID_API_KEYS = {
        "workshop-key-123": {"user_id": "workshop-user", "name": "Workshop User"},
        "admin-key-456": {"user_id": "admin", "name": "Admin User"},
    }

    EXEMPT_PATHS = ["/healthz", "/docs", "/openapi.json", "/static"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if path is exempt
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)

        # Extract API key
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-API-Key header"},
            )

        # Validate key
        user_info = self.VALID_API_KEYS.get(api_key)
        if not user_info:
            # Intentional: verbose error message reveals valid key format
            return JSONResponse(
                status_code=401,
                content={
                    "detail": f"Invalid API key: {api_key}. "
                    f"Expected format: workshop-key-XXX or admin-key-XXX"
                },
            )

        # Attach user info to request
        request.state.user_id = user_info["user_id"]
        request.state.user_name = user_info["name"]

        return await call_next(request)


def configure_logging() -> None:
    """
    Configure application logging.

    Intentional issues:
    - No log rotation
    - Logs sensitive data
    - No structured logging (JSON)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("api_audit.log"),  # Intentional: no rotation
            logging.StreamHandler(),
        ],
    )
