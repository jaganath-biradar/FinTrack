from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.models.income import Income
from app.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate

router = APIRouter(prefix="/api/income", tags=["Income"])


@router.post("/", response_model=IncomeRead, status_code=status.HTTP_201_CREATED)
def create_income(income_in: IncomeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income = Income(user_id=current_user.id, **income_in.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.get("/", response_model=List[IncomeRead])
def list_income(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    query = db.query(Income).filter(Income.user_id == current_user.id)
    if category:
        query = query.filter(Income.category == category)
    if start_date:
        query = query.filter(Income.income_date >= start_date)
    if end_date:
        query = query.filter(Income.income_date <= end_date)
    return query.order_by(Income.id.desc()).all()


@router.put("/{income_id}", response_model=IncomeRead)
def update_income(income_id: int, income_in: IncomeUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income = db.query(Income).filter(Income.id == income_id, Income.user_id == current_user.id).first()
    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    for field, value in income_in.model_dump().items():
        setattr(income, field, value)
    db.commit()
    db.refresh(income)
    return income


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_income(income_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income = db.query(Income).filter(Income.id == income_id, Income.user_id == current_user.id).first()
    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    db.delete(income)
    db.commit()
