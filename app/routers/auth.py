import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.auth.utils import authenticate_user, create_access_token, get_password_hash, get_user_by_email
from app.auth.csrf import get_csrf_token, verify_csrf
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut
import os

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])


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
        if get_user_by_email(db, email):
            return RedirectResponse(url="/register?error=exists", status_code=302)
        user = User(
            full_name=full_name,
            email=email,
            password_hash=get_password_hash(password),
        )
        db.add(user)
        db.commit()
        logger.info(f"User registered: {email}")
        return RedirectResponse(url="/login?registered=1", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"register_form error: {e}", exc_info=True)
        db.rollback()
        return RedirectResponse(url="/register?error=server", status_code=302)


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


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
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
