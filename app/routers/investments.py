from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.schemas.investment import InvestmentCreate, InvestmentRead, InvestmentUpdate
from app.crud import investment as crud_investment

router = APIRouter(prefix="/api/investments", tags=["Investments"])


@router.post("/", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
def create_investment(investment_in: InvestmentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_investment.create_investment(db, current_user.id, investment_in)


@router.get("/", response_model=List[InvestmentRead])
def list_investments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_investment.list_investments(db, current_user.id)


@router.put("/{investment_id}", response_model=InvestmentRead)
def update_investment(investment_id: int, investment_in: InvestmentUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    investment = crud_investment.get_investment(db, investment_id, current_user.id)
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment record not found")
    return crud_investment.update_investment(db, investment, investment_in)


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_investment(investment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    investment = crud_investment.get_investment(db, investment_id, current_user.id)
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment record not found")
    crud_investment.delete_investment(db, investment)
