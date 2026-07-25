import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.auth.utils import authenticate_user, create_access_token, get_password_hash, get_user_by_email, verify_password
from app.auth.csrf import get_csrf_token, verify_csrf
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut
from app.services.email_service import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])

_EMAIL_VERIFY_ENABLED = os.getenv("SMTP_USER", "") != ""


# ── Register form ─────────────────────────────────────────────
@router.post("/register-form")
@limiter.limit("10/minute")
def register_form(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        verify_csrf(request, csrf_token)
        if len(password) < 8:
            return RedirectResponse(url="/register?error=weak_password", status_code=302)
        existing = get_user_by_email(db, email)
        if existing:
            return RedirectResponse(url="/register?error=exists", status_code=302)
        verification_token = secrets.token_urlsafe(32) if _EMAIL_VERIFY_ENABLED else None
        user = User(
            full_name=full_name,
            email=email,
            password_hash=get_password_hash(password),
            is_verified=not _EMAIL_VERIFY_ENABLED,
            verification_token=verification_token,
        )
        db.add(user)
        db.commit()
        logger.info(f"User registered: {email}")
        if _EMAIL_VERIFY_ENABLED:
            send_verification_email(email, full_name, verification_token)
            return RedirectResponse(url="/login?registered=1&verify=1", status_code=302)
        return RedirectResponse(url="/login?registered=1", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"register_form error: {e}", exc_info=True)
        db.rollback()
        return RedirectResponse(url="/register?error=server", status_code=302)


# ── Login form ────────────────────────────────────────────────
@router.post("/login-form")
@limiter.limit("10/minute")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        verify_csrf(request, csrf_token)
        user = authenticate_user(db, username, password)
        if not user:
            return RedirectResponse(url="/login?error=invalid", status_code=302)
        if _EMAIL_VERIFY_ENABLED and not user.is_verified:
            return RedirectResponse(url="/login?error=unverified", status_code=302)
        access_token = create_access_token(data={"sub": user.email})
        response = RedirectResponse(url="/dashboard", status_code=302)
        is_secure = os.getenv("RENDER", "") != ""
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=is_secure,
            max_age=60 * int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"login_form error: {e}", exc_info=True)
        return RedirectResponse(url="/login?error=server", status_code=302)


# ── Email verification ────────────────────────────────────────
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        return RedirectResponse(url="/login?error=invalid_token", status_code=302)
    user.is_verified = True
    user.verification_token = None
    db.commit()
    logger.info(f"Email verified: {user.email}")
    return RedirectResponse(url="/login?verified=1", status_code=302)


# ── Forgot password ───────────────────────────────────────────
@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        verify_csrf(request, csrf_token)
        user = get_user_by_email(db, email)
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            db.commit()
            send_password_reset_email(email, user.full_name, token)
            logger.info(f"Password reset requested: {email}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"forgot_password error: {e}", exc_info=True)
    # Always redirect same way to prevent email enumeration
    return RedirectResponse(url="/login?reset=sent", status_code=302)


# ── Reset password ────────────────────────────────────────────
@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        verify_csrf(request, csrf_token)
        if len(password) < 8:
            return RedirectResponse(url=f"/auth/reset-password?token={token}&error=weak", status_code=302)
        user = db.query(User).filter(User.reset_token == token).first()
        if not user or not user.reset_token_expires:
            return RedirectResponse(url="/login?error=invalid_token", status_code=302)
        if datetime.now(timezone.utc) > user.reset_token_expires.replace(tzinfo=timezone.utc):
            return RedirectResponse(url="/login?error=expired_token", status_code=302)
        user.password_hash = get_password_hash(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        logger.info(f"Password reset completed: {user.email}")
        return RedirectResponse(url="/login?reset=done", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"reset_password error: {e}", exc_info=True)
        return RedirectResponse(url="/login?error=server", status_code=302)


# ── Logout ────────────────────────────────────────────────────
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ── API endpoints ─────────────────────────────────────────────
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": create_access_token(data={"sub": user.email}), "token_type": "bearer"}
