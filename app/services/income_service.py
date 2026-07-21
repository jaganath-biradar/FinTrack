from typing import List
from sqlalchemy.orm import Session
from app.crud import income as crud_income
from app.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate


def create_income(db: Session, user_id: int, income_in: IncomeCreate) -> IncomeRead:
    return crud_income.create_income(db, user_id, income_in)


def list_income(db: Session, user_id: int, category: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[IncomeRead]:
    return crud_income.list_income(db, user_id, category=category, start_date=start_date, end_date=end_date)


def get_income(db: Session, income_id: int, user_id: int):
    return crud_income.get_income(db, income_id, user_id)


def update_income(db: Session, income, income_in: IncomeUpdate):
    return crud_income.update_income(db, income, income_in)


def delete_income(db: Session, income):
    return crud_income.delete_income(db, income)
