from datetime import date
from pydantic import BaseModel, ConfigDict


class SavingsGoalBase(BaseModel):
    goal_name: str
    target_amount: float
    current_amount: float
    target_date: date
    status: str


class SavingsGoalCreate(SavingsGoalBase):
    pass


class SavingsGoalUpdate(SavingsGoalBase):
    pass


class SavingsGoalRead(SavingsGoalBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
