import os
import logging
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)
_CSRF_MAX_AGE = 3600  # 1 hour
_CSRF_VALUE = "csrf-valid"


def _serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")
    return URLSafeTimedSerializer(secret, salt="csrf-token")


def get_csrf_token(request: Request) -> str:
    return _serializer().dumps(_CSRF_VALUE)


def verify_csrf(request: Request, form_token: str) -> None:
    try:
        value = _serializer().loads(form_token, max_age=_CSRF_MAX_AGE)
        if value != _CSRF_VALUE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
    except (BadSignature, SignatureExpired) as e:
        logger.warning(f"CSRF validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
