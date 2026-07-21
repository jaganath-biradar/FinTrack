from typing import List
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, user_id: int, expense_in: ExpenseCreate) -> Expense:
    expense = Expense(user_id=user_id, **expense_in.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(db: Session, user_id: int, category: str | None = None, start_date: str | None = None, end_date: str | None = None) -> List[Expense]:
    query = db.query(Expense).filter(Expense.user_id == user_id)
    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    return query.order_by(Expense.id.desc()).all()


def get_expense(db: Session, expense_id: int, user_id: int) -> Expense | None:
    return db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()


def update_expense(db: Session, expense: Expense, expense_in: ExpenseUpdate) -> Expense:
    for field, value in expense_in.model_dump().items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()
