from typing import List
from sqlalchemy.orm import Session
from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentUpdate


def create_investment(db: Session, user_id: int, investment_in: InvestmentCreate) -> Investment:
    investment = Investment(user_id=user_id, **investment_in.model_dump())
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment


def list_investments(db: Session, user_id: int) -> List[Investment]:
    return db.query(Investment).filter(Investment.user_id == user_id).order_by(Investment.investment_date.desc()).all()


def get_investment(db: Session, investment_id: int, user_id: int) -> Investment | None:
    return db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == user_id).first()


def update_investment(db: Session, investment: Investment, investment_in: InvestmentUpdate) -> Investment:
    for field, value in investment_in.model_dump().items():
        setattr(investment, field, value)
    db.commit()
    db.refresh(investment)
    return investment


def delete_investment(db: Session, investment: Investment) -> None:
    db.delete(investment)
    db.commit()
