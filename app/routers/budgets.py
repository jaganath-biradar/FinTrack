from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.crud import budget as crud_budget

router = APIRouter(prefix="/api/budgets", tags=["Budget"])


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(budget_in: BudgetCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_budget.create_budget(db, current_user.id, budget_in)


@router.get("/", response_model=List[BudgetRead])
def list_budgets(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_budget.list_budgets(db, current_user.id)


@router.put("/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, budget_in: BudgetUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    budget = crud_budget.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return crud_budget.update_budget(db, budget, budget_in)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_budget(budget_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    budget = crud_budget.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    crud_budget.delete_budget(db, budget)
