from typing import List
from sqlalchemy.orm import Session
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeUpdate


def create_income(db: Session, user_id: int, income_in: IncomeCreate) -> Income:
    income = Income(user_id=user_id, **income_in.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


def list_income(db: Session, user_id: int, category: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[Income]:
    query = db.query(Income).filter(Income.user_id == user_id)
    if category:
        query = query.filter(Income.category == category)
    if start_date:
        query = query.filter(Income.income_date >= start_date)
    if end_date:
        query = query.filter(Income.income_date <= end_date)
    return query.order_by(Income.id.desc()).all()


def get_income(db: Session, income_id: int, user_id: int) -> Income | None:
    return db.query(Income).filter(Income.id == income_id, Income.user_id == user_id).first()


def update_income(db: Session, income: Income, income_in: IncomeUpdate) -> Income:
    for field, value in income_in.model_dump().items():
        setattr(income, field, value)
    db.commit()
    db.refresh(income)
    return income


def delete_income(db: Session, income: Income) -> None:
    db.delete(income)
    db.commit()
