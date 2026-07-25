import os
import logging
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)
_CSRF_MAX_AGE = 3600  # 1 hour


def _serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")
    return URLSafeTimedSerializer(secret, salt="csrf-token")


def generate_csrf_token(session_id: str) -> str:
    return _serializer().dumps(session_id)


def validate_csrf_token(token: str, session_id: str) -> bool:
    try:
        value = _serializer().loads(token, max_age=_CSRF_MAX_AGE)
        return value == session_id
    except (BadSignature, SignatureExpired) as e:
        logger.warning(f"CSRF validation failed: {e}")
        return False


def _fingerprint(request: Request) -> str:
    """Use real client IP (X-Forwarded-For on Render) + user-agent."""
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
    return ip + request.headers.get("user-agent", "")


def get_csrf_token(request: Request) -> str:
    return generate_csrf_token(_fingerprint(request))


def verify_csrf(request: Request, form_token: str) -> None:
    if not validate_csrf_token(form_token, _fingerprint(request)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
