from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.schemas.user import UserCreate


def create_user(db: Session, user_in: UserCreate, password_hash: str):
    return crud_user.create_user(db, user_in, password_hash)


def get_user_by_email(db: Session, email: str):
    return crud_user.get_user_by_email(db, email)
