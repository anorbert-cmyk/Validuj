from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.auth import create_csrf_token, create_session_token, hash_password, verify_password
from app.repository import create_user, get_user_by_email, list_users
from app.security import auth_rate_limit, require_admin, require_csrf, require_session
from app.schemas import LoginRequest, RegisterRequest


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
    role = "admin" if payload.email.strip().lower() == settings.admin_email.strip().lower() else "user"
    create_user(payload.email, hash_password(payload.password), role=role)
    token = create_session_token(settings, email=payload.email.strip().lower(), role=role)
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
    token = create_session_token(settings, email=user["email"], role=user["role"])
    _set_session_cookie(request, response, token, create_csrf_token())
    return {"email": user["email"], "role": user["role"]}


@router.post("/logout")
async def logout(response: Response, _: None = Depends(require_csrf)):
    response.delete_cookie("validuj_session")
    response.delete_cookie("validuj_csrf")
    return {"status": "logged_out"}


@router.get("/me")
async def me(session=Depends(require_session)):
    return session


@router.get("/admin/users")
async def admin_users(session=Depends(require_admin)):
    return [user.model_dump(mode="json") for user in list_users()]
