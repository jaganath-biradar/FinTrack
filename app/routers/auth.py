import os
import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth.utils import authenticate_user, create_access_token, get_password_hash, get_user_by_email
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-form")
def register_form(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"Register attempt: {email}")
        existing_user = get_user_by_email(db, email)
        if existing_user:
            return RedirectResponse(url="/register?error=exists", status_code=status.HTTP_302_FOUND)
        hashed = get_password_hash(password)
        user = User(full_name=full_name, email=email, password_hash=hashed)
        db.add(user)
        db.commit()
        logger.info(f"User registered: {email}")
        return RedirectResponse(url="/login?registered=1", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        logger.error(f"register_form error: {e}", exc_info=True)
        db.rollback()
        return RedirectResponse(url="/register?error=server", status_code=status.HTTP_302_FOUND)


@router.post("/login-form")
def login_form(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"Login attempt: {username}")
        user = authenticate_user(db, username, password)
        if not user:
            logger.warning(f"Login failed for: {username}")
            return RedirectResponse(url="/login?error=invalid", status_code=status.HTTP_302_FOUND)
        access_token = create_access_token(data={"sub": user.email})
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        is_secure = os.getenv("RENDER", "") != ""
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=is_secure,
            max_age=60 * int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        )
        logger.info(f"Login success: {username}, secure={is_secure}")
        return response
    except Exception as e:
        logger.error(f"login_form error: {e}", exc_info=True)
        return RedirectResponse(url="/login?error=server", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(data={"sub": user.email}), "token_type": "bearer"}
