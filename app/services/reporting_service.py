from sqlalchemy.orm import Session
from typing import Dict
from app.models.income import Income
from app.models.expense import Expense


def monthly_totals(db: Session, user_id: int, month: int, year: int) -> Dict[str, float]:
    incomes = db.query(Income).filter(Income.user_id == user_id).all()
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    income_total = sum(float(i.amount) for i in incomes if i.income_date.month == month and i.income_date.year == year)
    expense_total = sum(float(e.amount) for e in expenses if e.expense_date.month == month and e.expense_date.year == year)
    return {"income_total": income_total, "expense_total": expense_total}
