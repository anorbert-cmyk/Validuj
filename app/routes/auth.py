from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from datetime import datetime, timedelta, timezone

from app.auth import (
    SESSION_TTL_SECONDS,
    create_csrf_token,
    create_session_token_with_id,
    create_one_time_token,
    hash_password,
    verify_password,
)
from app.repository import (
    create_session_record,
    create_password_reset_token,
    create_user,
    consume_password_reset_token,
    get_user_by_email,
    list_sessions_for_email,
    list_users,
    revoke_session_record,
    update_user_password,
)
from app.security import auth_rate_limit, require_admin, require_csrf, require_session
from app.schemas import LoginRequest, PasswordResetConfirmRequest, PasswordResetRequest, RegisterRequest


router = APIRouter(prefix="/api/auth")


def _set_session_cookie(request: Request, response: Response, token: str, csrf_token: str) -> None:
    secure = request.app.state.settings.app_env == "production"
    response.set_cookie(
        "validuj_session",
        token,
        httponly=True,
        samesite="lax",
        secure=secure,
        max_age=60 * 60 * 24 * 7,
    )
    response.set_cookie(
        "validuj_csrf",
        csrf_token,
        httponly=False,
        samesite="lax",
        secure=secure,
        max_age=60 * 60 * 24 * 7,
    )


@router.post("/register")
async def register(
    request: Request,
    response: Response,
    payload: RegisterRequest,
    _: None = Depends(auth_rate_limit),
):
    existing = get_user_by_email(payload.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    settings = request.app.state.settings
    role = "user"
    if (
        payload.email.strip().lower() == settings.admin_email.strip().lower()
        and settings.admin_bootstrap_token
        and payload.bootstrap_token == settings.admin_bootstrap_token
    ):
        role = "admin"
    create_user(payload.email, hash_password(payload.password), role=role)
    session_id = create_csrf_token()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)
    create_session_record(session_id, payload.email.strip().lower(), role, expires_at.isoformat())
    token = create_session_token_with_id(
        settings,
        session_id=session_id,
        email=payload.email.strip().lower(),
        role=role,
    )
    _set_session_cookie(request, response, token, create_csrf_token())
    return {"email": payload.email.strip().lower(), "role": role}


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    _: None = Depends(auth_rate_limit),
):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    settings = request.app.state.settings
    session_id = create_csrf_token()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)
    create_session_record(session_id, user["email"], user["role"], expires_at.isoformat())
    token = create_session_token_with_id(
        settings,
        session_id=session_id,
        email=user["email"],
        role=user["role"],
    )
    _set_session_cookie(request, response, token, create_csrf_token())
    return {"email": user["email"], "role": user["role"]}


@router.post("/logout")
async def logout(response: Response, session=Depends(require_session), _: None = Depends(require_csrf)):
    revoke_session_record(session["sid"])
    response.delete_cookie("validuj_session")
    response.delete_cookie("validuj_csrf")
    return {"status": "logged_out"}


@router.get("/me")
async def me(session=Depends(require_session)):
    return session


@router.get("/admin/users")
async def admin_users(session=Depends(require_admin)):
    return [user.model_dump(mode="json") for user in list_users()]


@router.get("/sessions")
async def sessions(session=Depends(require_session)):
    return [record.model_dump(mode="json") for record in list_sessions_for_email(session["email"])]


@router.post("/request-reset")
async def request_reset(payload: PasswordResetRequest, _: None = Depends(auth_rate_limit)):
    user = get_user_by_email(payload.email)
    if user is None:
        return {"status": "ok"}
    token = create_one_time_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    create_password_reset_token(payload.email, token, expires_at.isoformat())
    return {
        "status": "ok",
        "reset_token": token,
        "expires_at": expires_at.isoformat(),
    }


@router.post("/reset-password")
async def reset_password(
    payload: PasswordResetConfirmRequest,
    _: None = Depends(auth_rate_limit),
):
    token_record = consume_password_reset_token(payload.token)
    if token_record is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    update_user_password(token_record["email"], hash_password(payload.password))
    return {"status": "password_updated"}
