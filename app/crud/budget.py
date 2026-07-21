from typing import List
from sqlalchemy.orm import Session
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate


def create_budget(db: Session, user_id: int, budget_in: BudgetCreate) -> Budget:
    budget = Budget(user_id=user_id, **budget_in.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session, user_id: int) -> List[Budget]:
    return db.query(Budget).filter(Budget.user_id == user_id).order_by(Budget.year.desc(), Budget.month.desc()).all()


def get_budget(db: Session, budget_id: int, user_id: int) -> Budget | None:
    return db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()


def update_budget(db: Session, budget: Budget, budget_in: BudgetUpdate) -> Budget:
    for field, value in budget_in.model_dump().items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget: Budget) -> None:
    db.delete(budget)
    db.commit()
