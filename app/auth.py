from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.config import Settings


PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 200_000
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${derived}"


def verify_password(password: str, password_hash: str) -> bool:
    if "$" not in password_hash:
        legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy, password_hash)

    try:
        scheme, iteration_str, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if scheme != PASSWORD_SCHEME:
        return False
    try:
        iterations = int(iteration_str)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(derived, expected)


def create_session_token(settings: Settings, *, email: str, role: str) -> str:
    return create_session_token_with_id(
        settings,
        session_id=secrets.token_urlsafe(18),
        email=email,
        role=role,
    )


def create_session_token_with_id(
    settings: Settings,
    *,
    session_id: str,
    email: str,
    role: str,
) -> str:
    payload = json.dumps(
        {
            "sid": session_id,
            "email": email,
            "role": role,
            "exp": int(time.time()) + SESSION_TTL_SECONDS,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    signature = hmac.new(settings.auth_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest().encode("utf-8")
    return (
        urlsafe_b64encode(payload).decode("utf-8").rstrip("=")
        + "."
        + urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    )


def create_csrf_token() -> str:
    return secrets.token_urlsafe(24)


def decode_session_token(settings: Settings, token: str) -> dict[str, str] | None:
    try:
        payload_part, signature_part = token.split(".", 1)
        payload = urlsafe_b64decode(_pad(payload_part))
        signature = urlsafe_b64decode(_pad(signature_part))
    except Exception:
        return None

    expected = hmac.new(settings.auth_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest().encode("utf-8")
    if not hmac.compare_digest(expected, signature):
        return None

    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    email = data.get("email")
    role = data.get("role")
    session_id = data.get("sid")
    exp = data.get("exp")
    if (
        not isinstance(email, str)
        or not isinstance(role, str)
        or not isinstance(session_id, str)
        or not isinstance(exp, int)
    ):
        return None
    if exp < int(time.time()):
        return None
    return {"sid": session_id, "email": email, "role": role}


def _pad(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode("utf-8")
