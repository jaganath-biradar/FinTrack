from typing import List
from sqlalchemy.orm import Session
from app.crud import expense as crud_expense
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate


def create_expense(db: Session, user_id: int, expense_in: ExpenseCreate) -> ExpenseRead:
    return crud_expense.create_expense(db, user_id, expense_in)


def list_expenses(db: Session, user_id: int, category: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[ExpenseRead]:
    return crud_expense.list_expenses(db, user_id, category=category, start_date=start_date, end_date=end_date)


def get_expense(db: Session, expense_id: int, user_id: int):
    return crud_expense.get_expense(db, expense_id, user_id)


def update_expense(db: Session, expense, expense_in: ExpenseUpdate):
    return crud_expense.update_expense(db, expense, expense_in)


def delete_expense(db: Session, expense):
    return crud_expense.delete_expense(db, expense)
