from __future__ import annotations

import hmac
import time
from collections import defaultdict, deque
from typing import TypedDict

from fastapi import Cookie, Header, HTTPException, Request

from app.auth import decode_session_token


class SessionUser(TypedDict):
    email: str
    role: str


_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def require_session(
    request: Request,
    validuj_session: str | None = Cookie(default=None),
) -> SessionUser:
    if not validuj_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = decode_session_token(request.app.state.settings, validuj_session)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session


def require_admin(
    request: Request,
    validuj_session: str | None = Cookie(default=None),
) -> SessionUser:
    session = require_session(request, validuj_session)
    if session["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return session


def require_csrf(
    validuj_csrf: str | None = Cookie(default=None),
    x_validuj_csrf: str | None = Header(default=None),
) -> None:
    if not validuj_csrf or not x_validuj_csrf:
        raise HTTPException(status_code=403, detail="Missing CSRF token")
    if not hmac.compare_digest(validuj_csrf, x_validuj_csrf):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def enforce_rate_limit(request: Request, *, scope: str, limit: int, window_seconds: int) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"{scope}:{client_host}"
    now = time.time()
    bucket = _RATE_LIMIT_BUCKETS[key]

    while bucket and bucket[0] <= now - window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {scope}")
    bucket.append(now)


def auth_rate_limit(request: Request) -> None:
    enforce_rate_limit(request, scope="auth", limit=10, window_seconds=60)


def mutation_rate_limit(request: Request) -> None:
    enforce_rate_limit(request, scope="mutation", limit=20, window_seconds=60)


def require_allowed_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    allowed = {
        request.app.state.settings.app_base_url.rstrip("/"),
        request.app.state.settings.frontend_base_url.rstrip("/"),
    }
    if origin and origin.rstrip("/") not in allowed:
        raise HTTPException(status_code=403, detail="Origin not allowed")
    if referer:
        if not any(referer.startswith(base) for base in allowed):
            raise HTTPException(status_code=403, detail="Referer not allowed")
