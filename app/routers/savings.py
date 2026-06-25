from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.models.savings_goal import SavingsGoal
from app.schemas.savings_goal import SavingsGoalCreate, SavingsGoalRead, SavingsGoalUpdate

router = APIRouter(prefix="/api/savings", tags=["Savings Goals"])


@router.post("/", response_model=SavingsGoalRead, status_code=status.HTTP_201_CREATED)
def create_savings_goal(goal_in: SavingsGoalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    goal = SavingsGoal(user_id=current_user.id, **goal_in.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/", response_model=List[SavingsGoalRead])
def list_savings_goals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).order_by(SavingsGoal.target_date).all()


@router.put("/{goal_id}", response_model=SavingsGoalRead)
def update_savings_goal(goal_id: int, goal_in: SavingsGoalUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings goal not found")
    for field, value in goal_in.model_dump().items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_savings_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings goal not found")
    db.delete(goal)
    db.commit()
