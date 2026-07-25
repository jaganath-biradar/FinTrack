import os
import logging
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import load_env
from app.database import get_db
from app.crud import user as crud_user
from app.models.user import User

load_env()

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def _secret_key() -> str:
    """Read SECRET_KEY fresh every call so Render env vars are always current."""
    key = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")
    return key


def _expire_minutes() -> int:
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"verify_password error: {e}")
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=_expire_minutes()))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _secret_key(), algorithm=ALGORITHM)


def get_user_by_email(db: Session, email: str):
    return crud_user.get_user_by_email(db, email)


def authenticate_user(db: Session, email: str, password: str):
    try:
        user = get_user_by_email(db, email)
        if not user:
            logger.warning(f"Login failed: user not found for {email}")
            return None
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed: wrong password for {email}")
            return None
        return user
    except Exception as e:
        logger.error(f"authenticate_user error: {e}")
        return None


def _extract_token(request: Request, bearer_token: str | None) -> str | None:
    token = bearer_token or request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        token = token[7:]
    return token or None


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Used by page routes. Raises 401 on failure — main.py handler redirects to /login."""
    raw = _extract_token(request, token)
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(raw, _secret_key(), algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def get_current_user_api(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Used by API routes. Returns 401 JSON on failure."""
    raw = _extract_token(request, token)
    _401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not raw:
        raise _401
    try:
        payload = jwt.decode(raw, _secret_key(), algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if not email:
            raise _401
    except JWTError:
        raise _401
    user = get_user_by_email(db, email)
    if user is None:
        raise _401
    return user
