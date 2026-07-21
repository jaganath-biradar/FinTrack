from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.utils import get_current_user_api as get_current_user
from app.database import get_db
from app.schemas.savings_goal import SavingsGoalCreate, SavingsGoalRead, SavingsGoalUpdate
from app.crud import savings_goal as crud_savings

router = APIRouter(prefix="/api/savings", tags=["Savings Goals"])


@router.post("/", response_model=SavingsGoalRead, status_code=status.HTTP_201_CREATED)
def create_savings_goal(goal_in: SavingsGoalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_savings.create_savings_goal(db, current_user.id, goal_in)


@router.get("/", response_model=List[SavingsGoalRead])
def list_savings_goals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud_savings.list_savings_goals(db, current_user.id)


@router.put("/{goal_id}", response_model=SavingsGoalRead)
def update_savings_goal(goal_id: int, goal_in: SavingsGoalUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    goal = crud_savings.get_savings_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings goal not found")
    return crud_savings.update_savings_goal(db, goal, goal_in)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_savings_goal(goal_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    goal = crud_savings.get_savings_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings goal not found")
    crud_savings.delete_savings_goal(db, goal)
