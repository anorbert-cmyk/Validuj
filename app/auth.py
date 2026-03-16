from __future__ import annotations

import hashlib
import hmac
import json
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.config import Settings


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def create_session_token(settings: Settings, *, email: str, role: str) -> str:
    payload = json.dumps({"email": email, "role": role}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(settings.auth_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest().encode("utf-8")
    return (
        urlsafe_b64encode(payload).decode("utf-8").rstrip("=")
        + "."
        + urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    )


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
    if not isinstance(email, str) or not isinstance(role, str):
        return None
    return {"email": email, "role": role}


def _pad(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode("utf-8")
