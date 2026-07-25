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


def get_csrf_token(request: Request) -> str:
    """Generate a CSRF token tied to the client IP + user-agent as session fingerprint."""
    fingerprint = request.client.host + request.headers.get("user-agent", "")
    return generate_csrf_token(fingerprint)


def verify_csrf(request: Request, form_token: str) -> None:
    """Raise 403 if CSRF token is invalid."""
    fingerprint = request.client.host + request.headers.get("user-agent", "")
    if not validate_csrf_token(form_token, fingerprint):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
