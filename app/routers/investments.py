from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentRead, InvestmentUpdate

router = APIRouter(prefix="/api/investments", tags=["Investments"])


@router.post("/", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
def create_investment(investment_in: InvestmentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    investment = Investment(user_id=current_user.id, **investment_in.model_dump())
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment


@router.get("/", response_model=List[InvestmentRead])
def list_investments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Investment).filter(Investment.user_id == current_user.id).order_by(Investment.investment_date.desc()).all()


@router.put("/{investment_id}", response_model=InvestmentRead)
def update_investment(investment_id: int, investment_in: InvestmentUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == current_user.id).first()
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment record not found")
    for field, value in investment_in.model_dump().items():
        setattr(investment, field, value)
    db.commit()
    db.refresh(investment)
    return investment


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_investment(investment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == current_user.id).first()
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment record not found")
    db.delete(investment)
    db.commit()
