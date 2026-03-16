from __future__ import annotations

from typing import TypedDict

from fastapi import Cookie, HTTPException, Request

from app.auth import decode_session_token


class SessionUser(TypedDict):
    email: str
    role: str


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
