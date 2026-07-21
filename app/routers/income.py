from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate
from app.services import income_service as svc_income

router = APIRouter(prefix="/api/income", tags=["Income"])


@router.post("/", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
def create_income(income_in: IncomeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return svc_income.create_income(db, current_user.id, income_in)


@router.get("/", response_model=List[IncomeRead])
def list_income(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return svc_income.list_income(db, current_user.id, category=category, start_date=start_date, end_date=end_date)


@router.put("/{income_id}", response_model=IncomeRead)
def update_income(income_id: int, income_in: IncomeUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income = svc_income.get_income(db, income_id, current_user.id)
    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    return svc_income.update_income(db, income, income_in)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_income(income_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income = svc_income.get_income(db, income_id, current_user.id)
    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    svc_income.delete_income(db, income)
