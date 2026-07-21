from typing import List
from sqlalchemy.orm import Session
from app.models.savings_goal import SavingsGoal
from app.schemas.savings_goal import SavingsGoalCreate, SavingsGoalUpdate


def create_savings_goal(db: Session, user_id: int, goal_in: SavingsGoalCreate) -> SavingsGoal:
    goal = SavingsGoal(user_id=user_id, **goal_in.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def list_savings_goals(db: Session, user_id: int) -> List[SavingsGoal]:
    return db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).order_by(SavingsGoal.target_date).all()


def get_savings_goal(db: Session, goal_id: int, user_id: int) -> SavingsGoal | None:
    return db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user_id).first()


def update_savings_goal(db: Session, goal: SavingsGoal, goal_in: SavingsGoalUpdate) -> SavingsGoal:
    for field, value in goal_in.model_dump().items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_savings_goal(db: Session, goal: SavingsGoal) -> None:
    db.delete(goal)
    db.commit()
