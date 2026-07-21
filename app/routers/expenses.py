from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services import expense_service as svc_expense

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return svc_expense.create_expense(db, current_user.id, expense_in)


@router.get("/", response_model=List[ExpenseRead])
def list_expenses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return svc_expense.list_expenses(db, current_user.id, category=category, start_date=start_date, end_date=end_date)


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, expense_in: ExpenseUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    expense = svc_expense.get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense entry not found")
    return svc_expense.update_expense(db, expense, expense_in)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_expense(expense_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    expense = svc_expense.get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense entry not found")
    svc_expense.delete_expense(db, expense)
