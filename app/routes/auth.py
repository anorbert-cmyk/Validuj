from __future__ import annotations

from fastapi import APIRouter, Cookie, HTTPException, Request, Response

from app.auth import create_session_token, decode_session_token, hash_password, verify_password
from app.repository import create_user, get_user_by_email, list_users
from app.schemas import LoginRequest, RegisterRequest


router = APIRouter(prefix="/api/auth")


@router.post("/register")
async def register(request: Request, response: Response, payload: RegisterRequest):
    existing = get_user_by_email(payload.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    settings = request.app.state.settings
    role = "admin" if payload.email.strip().lower() == settings.admin_email.strip().lower() else "user"
    create_user(payload.email, hash_password(payload.password), role=role)
    token = create_session_token(settings, email=payload.email.strip().lower(), role=role)
    response.set_cookie("validuj_session", token, httponly=True, samesite="lax")
    return {"email": payload.email.strip().lower(), "role": role}


@router.post("/login")
async def login(request: Request, response: Response, payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    settings = request.app.state.settings
    token = create_session_token(settings, email=user["email"], role=user["role"])
    response.set_cookie("validuj_session", token, httponly=True, samesite="lax")
    return {"email": user["email"], "role": user["role"]}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("validuj_session")
    return {"status": "logged_out"}


@router.get("/me")
async def me(request: Request, validuj_session: str | None = Cookie(default=None)):
    if not validuj_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = decode_session_token(request.app.state.settings, validuj_session)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session


@router.get("/admin/users")
async def admin_users(request: Request, validuj_session: str | None = Cookie(default=None)):
    if not validuj_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = decode_session_token(request.app.state.settings, validuj_session)
    if session is None or session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return [user.model_dump(mode="json") for user in list_users()]
